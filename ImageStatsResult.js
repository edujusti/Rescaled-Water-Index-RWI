// Look for São Paulo, Curitiba, Florianópolis, Porto Alegre, Buenos Aires and Viña del Mar

var saoPaulo = {
  divider:   5.828770268246491,
  RWI_T:     0.6156771100334373,
  MNDWI_T:   0.4020156774916013,
  NDWI_T:    0.3603082851637765,
}

var curitiba = {
  divider:   5.85892560490295,
  RWI_T:     0.37468758552409387,
  MNDWI_T:   0.5236883942766296,
  NDWI_T:    0.54,
}

var florianopolis = {
  divider:    5.877213189872267,
  RWI_T: 0.3106312961397413,
  MNDWI_T   : 0.4338894250654901,
  NDWI_T    : 0.2883031301482702,
}

var portoAlegre = {
  divider:    5.672592996509505,
  RWI_T: 0.4289478426998933,
  MNDWI_T   : 0.4803625377643504,
  NDWI_T    : 0.3811659192825112,
}

var buenosAires = {
  divider:    5.877213189872267,
  RWI_T: 0.5222763705494408,
  MNDWI_T   : 0.5135869565217391,
  NDWI_T    : 0.4080338266384778,
}

var vinaDelMar = {
  divider:    5.2392623813178965,
  RWI_T: 0.36133600909323765,
  MNDWI_T   : 0.4308943089430894,
  NDWI_T    : 0.3594202898550724,
}

var shadowWater = ee.FeatureCollection('projects/ee-efjustiniano/assets/doutorado/waterIndex/shadowWater')
var rectangle = ee.FeatureCollection('projects/ee-efjustiniano/assets/doutorado/waterIndex/waterShadowRectangle')
 
var e = Math.exp(1);
//print(e)
var pot = ee.Number(1 / e);
//print(pot)

var S2 = ee.ImageCollection('projects/ee-efjustiniano/assets/doutorado/waterIndex/cities_harmonized')
  .median()
  .select(['B2', 'B3', 'B4', 'B8', 'B11'])
  .divide(10000)
  .clip(rectangle)
  ;

var ndwi  = S2.normalizedDifference(['B3', 'B8']).rename('NDWI').toDouble();
var mndwi = S2.normalizedDifference(['B3', 'B11']).rename('MNDWI').toDouble();

S2 = S2.addBands(ndwi).addBands(mndwi)

Map.addLayer(S2, {bands: ["B3","B8","B11"], gamma: 1.3, min: 0.01, max:0.386, opacity:1}, 'Sentinel 3 8 11', false);
Map.addLayer(S2, {bands: ["B4","B3","B2"],  gamma: 1,   min: 0.01, max:0.224, opacity:1}, 'Sentinel 2 3 4');

var areas = ['saoPaulo', 'curitiba', 'florianopolis', 'portoAlegre', 'buenosAires', 'vinaDelMar']

function selectDictionary(dictName) {
  var dictionaries = {
    saoPaulo: saoPaulo,
    curitiba: curitiba,
    florianopolis: florianopolis,
    portoAlegre: portoAlegre,
    buenosAires: buenosAires,
    vinaDelMar: vinaDelMar
  };
  return dictionaries[dictName];
}

function getDictionaryValue(dictionary, key) {
  return dictionary[key];
}

areas.map(function(area){
  var areaSelected = rectangle.filter(ee.Filter.eq('city2', area))
  var S2Selected = S2.clip(areaSelected)

  var dict = selectDictionary(area)

  var green = S2Selected.select('B3')
  var swir  = S2Selected.select('B11')
  var divider = getDictionaryValue(dict, 'divider')
  var greenPot = (green.pow(pot)).divide(divider);
  var water = (greenPot.subtract(swir)).divide(greenPot.add(swir)).rename('RWI').toDouble();

  var RWI_T = getDictionaryValue(dict, 'RWI_T')
  var MNDWI_T = getDictionaryValue(dict, 'MNDWI_T')
  var NDWI_T = getDictionaryValue(dict, 'NDWI_T')

  var mask_ndwiTemp = S2Selected.select('NDWI').gt(NDWI_T)
  var mask_ndwi = mask_ndwiTemp.updateMask(mask_ndwiTemp)
  Map.addLayer(mask_ndwi, {palette: ["4df7ff"]}, 'NDWI - '+area, false);
  
  var mask_mndwiTemp = S2Selected.select('MNDWI').gt(MNDWI_T)
  var mask_mndwi = mask_mndwiTemp.updateMask(mask_mndwiTemp)
  Map.addLayer(mask_mndwi, {palette: ["4df7ff"]}, 'MNDWI - '+area, false);
  
  var mask_rwiTemp = water.select('RWI').gt(RWI_T)
  var mask_rwi = mask_rwiTemp.updateMask(mask_rwiTemp)
  Map.addLayer(mask_rwi, {palette: ["4df7ff"]}, 'waterLog - '+area, false);
})
