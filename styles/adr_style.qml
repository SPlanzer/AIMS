<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="1.7.0-Wroclaw" minimumScale="0" maximumScale="1e+08" hasScaleBasedVisibilityFlag="0">
  <transparencyLevelInt>255</transparencyLevelInt>
  <renderer-v2 attr="status" symbollevels="0" type="categorizedSymbol">
    <categories>
      <category symbol="5" value="BADR" label="Bad road name"/>
      <category symbol="6" value="BADN" label="Bad number format"/>
      <category symbol="4" value="UNKN" label="Undefined"/>
      <category symbol="1" value="NEWA" label="New address"/>
      <category symbol="3" value="REPL" label="Replace"/>
      <category symbol="2" value="DELE" label="Delete"/>
      <category symbol="0" value="IGNR" label="Ignore"/>
    </categories>
    <symbols>
      <symbol outputUnit="MM" alpha="1" type="marker" name="0">
        <layer pass="0" class="SimpleMarker" locked="0">
          <prop k="angle" v="0"/>
          <prop k="color" v="255,255,255,255"/>
          <prop k="color_border" v="0,0,0,255"/>
          <prop k="name" v="circle"/>
          <prop k="offset" v="0,0"/>
          <prop k="size" v="2"/>
        </layer>
      </symbol>
      <symbol outputUnit="MM" alpha="1" type="marker" name="1">
        <layer pass="0" class="SimpleMarker" locked="0">
          <prop k="angle" v="0"/>
          <prop k="color" v="84,255,0,255"/>
          <prop k="color_border" v="0,0,0,255"/>
          <prop k="name" v="circle"/>
          <prop k="offset" v="0,0"/>
          <prop k="size" v="2"/>
        </layer>
      </symbol>
      <symbol outputUnit="MM" alpha="1" type="marker" name="2">
        <layer pass="0" class="SimpleMarker" locked="0">
          <prop k="angle" v="0"/>
          <prop k="color" v="0,0,0,255"/>
          <prop k="color_border" v="0,0,0,255"/>
          <prop k="name" v="circle"/>
          <prop k="offset" v="0,0"/>
          <prop k="size" v="2"/>
        </layer>
      </symbol>
      <symbol outputUnit="MM" alpha="1" type="marker" name="3">
        <layer pass="0" class="SimpleMarker" locked="0">
          <prop k="angle" v="0"/>
          <prop k="color" v="0,170,0,255"/>
          <prop k="color_border" v="0,0,0,255"/>
          <prop k="name" v="circle"/>
          <prop k="offset" v="0,0"/>
          <prop k="size" v="2"/>
        </layer>
      </symbol>
      <symbol outputUnit="MM" alpha="1" type="marker" name="4">
        <layer pass="0" class="SimpleMarker" locked="0">
          <prop k="angle" v="0"/>
          <prop k="color" v="255,0,0,255"/>
          <prop k="color_border" v="0,0,0,255"/>
          <prop k="name" v="circle"/>
          <prop k="offset" v="0,0"/>
          <prop k="size" v="2"/>
        </layer>
      </symbol>
      <symbol outputUnit="MM" alpha="1" type="marker" name="5">
        <layer pass="0" class="SimpleMarker" locked="0">
          <prop k="angle" v="0"/>
          <prop k="color" v="255,0,0,255"/>
          <prop k="color_border" v="0,0,0,255"/>
          <prop k="name" v="regular_star"/>
          <prop k="offset" v="0,0"/>
          <prop k="size" v="5"/>
        </layer>
      </symbol>
      <symbol outputUnit="MM" alpha="1" type="marker" name="6">
        <layer pass="0" class="SimpleMarker" locked="0">
          <prop k="angle" v="0"/>
          <prop k="color" v="255,127,0,255"/>
          <prop k="color_border" v="0,0,0,255"/>
          <prop k="name" v="regular_star"/>
          <prop k="offset" v="0,0"/>
          <prop k="size" v="5"/>
        </layer>
      </symbol>
    </symbols>
    <source-symbol>
      <symbol outputUnit="MM" alpha="1" type="marker" name="0">
        <layer pass="0" class="SimpleMarker" locked="0">
          <prop k="angle" v="0"/>
          <prop k="color" v="137,64,44,255"/>
          <prop k="color_border" v="0,0,0,255"/>
          <prop k="name" v="circle"/>
          <prop k="offset" v="0,0"/>
          <prop k="size" v="2"/>
        </layer>
      </symbol>
    </source-symbol>
    <colorramp type="gradient" name="[source]">
      <prop k="color1" v="0,176,126,255"/>
      <prop k="color2" v="255,0,0,255"/>
      <prop k="stops" v="0.25;0,255,0,255:0.5;255,255,0,255"/>
    </colorramp>
    <rotation field=""/>
    <sizescale field=""/>
  </renderer-v2>
  <customproperties/>
  <displayfield>src_roadname</displayfield>
  <label>1</label>
  <labelfield>housenumber</labelfield>
  <labelattributes>
    <label fieldname="housenumber" text=""/>
    <family fieldname="" name="MS Shell Dlg 2"/>
    <size fieldname="" units="pt" value="10"/>
    <bold fieldname="" on="0"/>
    <italic fieldname="" on="0"/>
    <underline fieldname="" on="0"/>
    <strikeout fieldname="" on="0"/>
    <color fieldname="" red="0" blue="0" green="0"/>
    <x fieldname=""/>
    <y fieldname=""/>
    <offset x="-5" y="0" units="pt" yfieldname="" xfieldname=""/>
    <angle fieldname="" value="0" auto="0"/>
    <alignment fieldname="" value="aboveleft"/>
    <buffercolor fieldname="" red="255" blue="255" green="255"/>
    <buffersize fieldname="" units="pt" value="1"/>
    <bufferenabled fieldname="" on=""/>
    <multilineenabled fieldname="" on=""/>
    <selectedonly on=""/>
  </labelattributes>
  <edittypes>
    <edittype type="10" name="adr_id"/>
    <edittype type="10" name="cluster_id"/>
    <edittype type="0" name="housenumber"/>
    <edittype type="11" name="ismerged"/>
    <edittype type="10" name="job_id"/>
    <edittype type="11" name="linked"/>
    <edittype type="11" name="mbk_id"/>
    <edittype type="11" name="merge_adr_id"/>
    <edittype type="0" name="notes"/>
    <edittype type="11" name="par_id"/>
    <edittype type="11" name="par_sad_count"/>
    <edittype type="11" name="rcl_id"/>
    <edittype type="11" name="rna_id"/>
    <edittype type="11" name="sad_id"/>
    <edittype type="11" name="sad_par_id"/>
    <edittype type="11" name="src_housenumber"/>
    <edittype type="10" name="src_id"/>
    <edittype type="11" name="src_roadname"/>
    <edittype type="11" name="src_shape"/>
    <edittype type="11" name="src_status"/>
    <edittype type="10" name="status"/>
    <edittype type="10" name="warning_codes"/>
    <edittype type="11" name="warnings_accepted"/>
  </edittypes>
  <editform></editform>
  <editforminit></editforminit>
  <annotationform></annotationform>
  <attributeactions/>
</qgis>
