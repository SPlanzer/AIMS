<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="1.8.0-Lisboa" minimumScale="0" maximumScale="20000" hasScaleBasedVisibilityFlag="1">
  <transparencyLevelInt>255</transparencyLevelInt>
  <renderer-v2 attr="status" symbollevels="1" type="categorizedSymbol">
    <categories>
      <category symbol="0" value="APPR" label="APPR"/>
      <category symbol="1" value="CURR" label="CURR"/>
      <category symbol="2" value="PEND" label="PEND"/>
    </categories>
    <symbols>
      <symbol outputUnit="MM" alpha="0.498039" type="fill" name="0">
        <layer pass="0" class="SimpleFill" locked="0">
          <prop k="color" v="247,251,255,127"/>
          <prop k="color_border" v="150,255,138,127"/>
          <prop k="offset" v="0,0"/>
          <prop k="style" v="no"/>
          <prop k="style_border" v="solid"/>
          <prop k="width_border" v="0.5"/>
        </layer>
      </symbol>
      <symbol outputUnit="MM" alpha="1" type="fill" name="1">
        <layer pass="1" class="SimpleFill" locked="0">
          <prop k="color" v="255,255,255,255"/>
          <prop k="color_border" v="200,200,255,255"/>
          <prop k="offset" v="0,0"/>
          <prop k="style" v="no"/>
          <prop k="style_border" v="solid"/>
          <prop k="width_border" v="0.26"/>
        </layer>
      </symbol>
      <symbol outputUnit="MM" alpha="0.498039" type="fill" name="2">
        <layer pass="0" class="SimpleFill" locked="0">
          <prop k="color" v="112,163,195,127"/>
          <prop k="color_border" v="255,117,119,127"/>
          <prop k="offset" v="0,0"/>
          <prop k="style" v="no"/>
          <prop k="style_border" v="solid"/>
          <prop k="width_border" v="0.5"/>
        </layer>
      </symbol>
    </symbols>
    <source-symbol>
      <symbol outputUnit="MM" alpha="1" type="fill" name="0">
        <layer pass="0" class="SimpleFill" locked="0">
          <prop k="color" v="64,61,201,255"/>
          <prop k="color_border" v="0,0,0,255"/>
          <prop k="offset" v="0,0"/>
          <prop k="style" v="no"/>
          <prop k="style_border" v="solid"/>
          <prop k="width_border" v="0.3"/>
        </layer>
      </symbol>
    </source-symbol>
    <colorramp type="gradient" name="[source]">
      <prop k="color1" v="247,251,255,255"/>
      <prop k="color2" v="8,48,107,255"/>
      <prop k="stops" v="0.13;222,235,247,255:0.26;198,219,239,255:0.39;158,202,225,255:0.52;107,174,214,255:0.65;66,146,198,255:0.78;33,113,181,255:0.9;8,81,156,255"/>
    </colorramp>
    <rotation field=""/>
    <sizescale field=""/>
  </renderer-v2>
  <customproperties>
    <property key="ElectoralAddressLoader.Id" value="par"/>
  </customproperties>
  <displayfield>id</displayfield>
  <label>0</label>
  <labelattributes>
    <label fieldname="" text="Label"/>
    <family fieldname="" name="MS Shell Dlg 2"/>
    <size fieldname="" units="pt" value="12"/>
    <bold fieldname="" on="0"/>
    <italic fieldname="" on="0"/>
    <underline fieldname="" on="0"/>
    <strikeout fieldname="" on="0"/>
    <color fieldname="" red="0" blue="0" green="0"/>
    <x fieldname=""/>
    <y fieldname=""/>
    <offset x="0" y="0" units="pt" yfieldname="" xfieldname=""/>
    <angle fieldname="" value="0" auto="0"/>
    <alignment fieldname="" value="center"/>
    <buffercolor fieldname="" red="255" blue="255" green="255"/>
    <buffersize fieldname="" units="pt" value="1"/>
    <bufferenabled fieldname="" on=""/>
    <multilineenabled fieldname="" on=""/>
    <selectedonly on=""/>
  </labelattributes>
  <edittypes>
    <edittype type="0" name="alt_id"/>
    <edittype type="0" name="appellation_date"/>
    <edittype type="0" name="area"/>
    <edittype type="0" name="audit_id"/>
    <edittype type="0" name="calculated_area"/>
    <edittype type="0" name="fen_id"/>
    <edittype type="0" name="id"/>
    <edittype type="0" name="img_id"/>
    <edittype type="0" name="ldt_loc_id"/>
    <edittype type="0" name="nonsurvey_def"/>
    <edittype type="0" name="parcel_intent"/>
    <edittype type="0" name="status"/>
    <edittype type="0" name="toc_code"/>
    <edittype type="0" name="total_area"/>
  </edittypes>
  <editform></editform>
  <editforminit></editforminit>
  <annotationform></annotationform>
  <attributeactions/>
</qgis>
