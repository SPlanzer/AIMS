import sys
import re
import unicodedata
from Error import Error

class FieldEvaluator( object ):

    def __init__( self, definition='',mapfunc=None):
        self._func = lambda x: ''
        self._variables = dict()
        self._varchar = '@'
        revar = re.escape(self._varchar)
        revar = revar + r"\d+" + revar
        reprm = r"(" + revar + r"|\w+)"
        self._reprm = re.compile(reprm)
        reprmlist = r"\s*((?:"+reprm+r"(?:\s+"+reprm+r")*)?)\s*"
        self._reprmlist = re.compile(reprmlist)
        refunc = r"(\w+)\(" + reprmlist + r"\)"
        self._refunc = re.compile(refunc)

        if not mapfunc:
            mapfunc = lambda type,key,default: default
        self._mapping = mapfunc
        self.loadDefinition( definition )

    def loadDefinition(self,definition):
        self._func = lambda x: ''
        self._nfunc = 0
        self._funcs = dict()

        spacefunc = self._stringfunc(' ')
        # Convert strings
        definition = re.sub(r"(\'(?:[^\']+|\'\')*\')",lambda m: self._stringfunc(m.group(0)),definition)
        definition = re.sub(r'(\"(?:[^\"]+|\"\")*\")',lambda m: self._stringfunc(m.group(0)),definition)
        # Insert space between adjacent fields
        definition = re.sub(r"(\w|\))\s+(\w|\()",r"\1 "+spacefunc+r" \2",definition)
        # Now can get rid of any commas used to space fields
        definition = re.sub(r"\,"," ",definition)

        # Replace xxxx/yyyy with lookup('yyyy',xxxx)
        definition = re.sub(
            r"\b(\w+)\/(\w+)\b",
            lambda m: "lookup("+self._stringfunc(m.group(2))+" "+m.group(1)+" "+m.group(1)+")",
            definition)

        # Sort out function definitions
        while( True ):
            definition, count = self._refunc.subn(
                lambda m: self._addfunc(self._funcdef(m.group(1),m.group(2))),
                definition
                )
            if not count:
                break

        # Should be left with a list of parameters
        m = self._reprmlist.match(definition)
        if not m or m.group(0) != definition:
            raise Error("Invalid field definition " + definition)

        # Compute a function joining the fields
        self._func = self._funcdef('join',definition)

    def evaluator( self ):
        return self.evaluate

    def evaluate(self,varfunc):
        for k in self._variables:
            k = [self.unicode2ascii(entry) for entry in k] if isinstance(k,tuple) else self.unicode2ascii(k)
            self._variables[k] = varfunc(k)
        return self._func()

    def unicode2ascii(self,uni):
        return unicodedata.normalize('NFKD',uni).encode('ascii','ignore')

    # Define a mapping function to be used by a subclass

    def setMappingFunc( self, mapfunc ):
        """ Define an object used for looking up values

            Object must implement function call with 
            parameters type, key, default
        """
        self._mapping = mapfunc

    def _addfunc( self, f ):
        self._nfunc += 1
        name = self._varchar+str(self._nfunc)+self._varchar
        self._funcs[name] = f
        return name

    def _stringfunc(self, value):
        quote = value[0]
        if quote in "'\"":
            value = value[1:-1]
            value = value.replace(quote+quote,quote)
        return self._addfunc( lambda: value)

    def _varfunc(self, value):
        if value not in self._variables:
            self._variables[value] = ''
        return lambda: self._variables[value]

    def _listfunc( self, prmlist,nprm=-1):
        if not self._reprmlist.match(prmlist):
            raise Error("Invalid list definition: "+prmlist)
        flist=[]
        nfunc = 0
        for m in self._reprm.findall(prmlist):
            if nprm >= 0 and len(flist) == nprm:
                break
            if m[0] == self._varchar:
                flist.append(self._funcs[m])
            else:
                flist.append(self._varfunc(m))
        while len(flist) < nprm:
            flist.append(None)
        return lambda : [f() if f else '' for f in flist]

    def _funcdef( self, funcname, prmlist ):
        funcname = funcname.lower() or 'join'
        f=None
        nprm=-1
        if funcname == 'join':
            f = lambda p: ''.join(p)
        elif funcname == 'if':
            nprm = 3
            f = lambda p: p[1] if p[0] else p[2]
        elif funcname == 'replace':
            nprm = 3
            f = lambda p: re.sub(p[0],p[1],p[2])
        elif funcname == 'lookup':
            nprm = 3
            f = lambda p: self._mapping(p[0],p[1],p[2])
        else:
            raise Error("Invalid function name " + funcname)
        prms = self._listfunc(prmlist,nprm)
        return lambda : f(prms())
