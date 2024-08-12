// Look for the cities bellow

var cityGeometries = {
  'brasilia': ee.Geometry.Rectangle([     -47.91607, -15.74159,  -47.75937, -15.81345]),
  'milwaukee': ee.Geometry.Rectangle([    -88.54220,  43.14580,  -87.85283,  42.99279]),
  'sanFrancisco': ee.Geometry.Rectangle([-122.54849,  37.95127, -122.00124,  37.68820]),
  'alexandria': ee.Geometry.Rectangle([    29.82941,  31.43841,   30.70724,  31.09977]),
  'Mossaka': ee.Geometry.Rectangle([       16.45516,  -1.00517,   17.58675,  -1.62436]),
  'xangai': ee.Geometry.Rectangle([       120.24079,  31.55598,  121.66901,  31.05614]),
  'bombaim': ee.Geometry.Rectangle([       72.81561,  19.08333,   73.06521,  18.97396]),
  'melbourne': ee.Geometry.Rectangle([    144.34314, -37.82881,  145.67936, -38.42190]),
  'liverpool': ee.Geometry.Rectangle([     -3.05151,  53.45668,   -2.79431,  53.37445]),
}

Map.setCenter(-2.98949, 53.39702, 12)

var e = Math.exp(1);
//print(e)
var pot = ee.Number(1 / e);
//print(pot)

function S2_MNDWI(image) {
  var mndwi = image.normalizedDifference(['B3', 'B11']).rename('MNDWI').toDouble();
  return image.addBands(mndwi);
}

function L9_b3Pot(image) {
  var b3pot = image.select('SR_B3').pow(pot).rename('B3Pot');
  return image.addBands(b3pot);
}

function L9_MNDWI(image) {
  var mndwi = image.normalizedDifference(['SR_B3', 'SR_B6']).rename('MNDWI').toDouble();
  return image.addBands(mndwi);
}

function applyScaleFactors(image) {
  var opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2);
  var thermalBands = image.select('ST_B.*').multiply(0.00341802).add(149.0);
  return image.addBands(opticalBands, null, true)
              .addBands(thermalBands, null, true);
}

Object.keys(cityGeometries).forEach(function(city) {
  var geometry = cityGeometries[city];

  var S2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(geometry)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE',10))
    .filterDate('2022-01-01', '2024-06-30')
    .median()
    .select(['B2', 'B3', 'B4', 'B11'])
    .divide(10000)
    .clip(geometry)
    ;

  var S2_b3pot = S2.select('B3').pow(pot).rename('B3Pot')
  var S2_MNDWI = S2.normalizedDifference(['B3', 'B11']).rename('MNDWI').toDouble();
  
  S2 = S2.addBands(S2_b3pot).addBands(S2_MNDWI).select(['B2', 'B3', 'B3Pot', 'B4', 'B11', 'MNDWI'])
  
  var S2median = S2.select('B3', 'B3Pot').reduceRegion({
    reducer: ee.Reducer.median(),
    geometry: geometry,
    scale: 10,
    maxPixels: 1e9
  });

  var S2divider = ee.Number(S2median.get('B3Pot')).divide(ee.Number(S2median.get('B3')))
  //print('Sentinel-2 divider', city, S2divider)
  
  var S2_RWI = (S2.select('B3Pot').divide(S2divider).subtract(S2.select('B11'))).divide(S2.select('B3Pot').divide(S2divider).add(S2.select('B11')))
    .rename('RWI')
    .addBands(S2.select('MNDWI'))

  var S2_minMax = S2_RWI.select('RWI', 'MNDWI').reduceRegion({
    reducer: ee.Reducer.minMax(),
    geometry: geometry,
    scale: 10,
    maxPixels: 1e9
  });
  
  //print('Sentinel-2 minMax', S2_minMax)

  Map.addLayer(S2_RWI.select('RWI'),   {min: -1, max: 1}, city+' - Sentinel-2 - RWI',   false);
  Map.addLayer(S2_RWI.select('MNDWI'), {min: -1, max: 1}, city+' - Sentinel-2 - MNDWI', false);

  var L9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2')
    .filterBounds(geometry)
    .filterDate('2022-01-01', '2024-06-30')
    .filterMetadata('CLOUD_COVER', 'less_than', 10)
    .map(applyScaleFactors)
    .median()
    .clip(geometry)
    ;
    
  var L9_b3pot = L9.select('SR_B3').pow(pot).rename('B3Pot');
  var L9_mndwi = L9.normalizedDifference(['SR_B3', 'SR_B6']).rename('MNDWI').toDouble();
  
  L9 = L9.addBands(L9_b3pot).addBands(L9_mndwi).select(['SR_B2', 'SR_B3', 'B3Pot', 'SR_B4', 'SR_B6', 'MNDWI'])
    
  var L9median = L9.select('SR_B3', 'B3Pot').reduceRegion({
    reducer: ee.Reducer.median(),
    geometry: geometry,
    scale: 30,
    maxPixels: 1e9
  });

  var L9divider = ee.Number(L9median.get('B3Pot')).divide(ee.Number(L9median.get('SR_B3')))
  //print('Landsat-9 divider', city, L9divider)
  
  var L9_RWI = (L9.select('B3Pot').divide(L9divider).subtract(L9.select('SR_B6'))).divide(L9.select('B3Pot').divide(L9divider).add(L9.select('SR_B6')))
    .rename('RWI')
    .addBands(L9.select('MNDWI'))

  var L9_minMax = L9_RWI.select('RWI', 'MNDWI').reduceRegion({
    reducer: ee.Reducer.minMax(),
    geometry: geometry,
    scale: 30,
    maxPixels: 1e9
  });
  
  //print('Landsat-9 minMax', city, L9_minMax)

  Map.addLayer(L9_RWI.select('RWI'),   {min: -1, max: 1, opacity:1}, city+' - Landsat-9 - RWI',   false);
  Map.addLayer(L9_RWI.select('MNDWI'), {min: -1, max: 1, opacity:1}, city+' - Landsat-9 - MNDWI', false);

})
