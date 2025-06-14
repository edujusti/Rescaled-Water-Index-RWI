var start = '2023-01-01';
var end   = '2023-12-31';

var map = ui.Map();

var e = Math.exp(1);
var pot = ee.Number(1 / e);

function L9_b3Pot(image) {
  var b3pot = image.select('SR_B3').pow(pot).rename('B3Pot');
  return image.addBands(b3pot);
}

function applyScaleFactors(image) {
  var opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2);
  var thermalBands = image.select('ST_B.*').multiply(0.00341802).add(149.0);
  return image.addBands(opticalBands, null, true)
              .addBands(thermalBands, null, true);
}

function cloudMask(image) {
  var cloudShadowBitMask = 1 << 3;
  var cloudsBitMask = 1 << 5;
  var qa = image.select("QA_PIXEL");
  var mask = qa.bitwiseAnd(cloudShadowBitMask).eq(0)
               .and(qa.bitwiseAnd(cloudsBitMask).eq(0));
  return image.updateMask(mask).copyProperties(image, ["system:time_start"]);
}

// Function to display data from the selected area
function showArea(areaName) {
  var selected = area.filter(ee.Filter.eq('area', areaName));
  var geom = selected.geometry();

  map.centerObject(selected, 13);
  map.clear();
  
  function cut(image) {
    return image.clip(geom);
  }

  var L9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2')
      .filterDate(start, end)
      .filterBounds(geom)
      .filterMetadata('CLOUD_COVER', 'less_than', 30)
      .map(cloudMask)
      .map(applyScaleFactors)
      .map(cut);

  var L8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
      .filterDate(start, end)
      .filterBounds(geom)
      .filterMetadata('CLOUD_COVER', 'less_than', 30)
      .map(cloudMask)
      .map(applyScaleFactors)
      .map(cut);

  var Landsat = L9.merge(L8);
  var imagem = Landsat.median().clip(geom);

  Landsat.size().evaluate(function(size) {
    if (size === 0) {
      print('⚠️ No Landsat images found in 2023.');
      return;
    }

    map.addLayer(imagem, {bands: ["SR_B4", "SR_B3", "SR_B2"], min: 0.015, max: 0.2}, 'Landsat RGB');

    var image_b3pot = imagem.select('SR_B3').pow(pot).rename('B3Pot');
    imagem = imagem.addBands(image_b3pot);

    var medians = imagem.select('SR_B3', 'B3Pot').reduceRegion({
      reducer: ee.Reducer.median(),
      geometry: geom,
      scale: 30,
      maxPixels: 1e9
    });

    var LDivider = ee.Number(medians.get('B3Pot')).divide(ee.Number(medians.get('SR_B3')));

    var rwi = imagem.select('B3Pot').divide(LDivider)
      .subtract(imagem.select('SR_B6'))
      .divide(imagem.select('B3Pot').divide(LDivider).add(imagem.select('SR_B6')))
      .rename('RWI');

    var mndwi = imagem.select('SR_B3').subtract(imagem.select('SR_B6'))
      .divide(imagem.select('SR_B3').add(imagem.select('SR_B6')))
      .rename('MNDWI');

    var ndwi = imagem.select('SR_B3').subtract(imagem.select('SR_B5'))
      .divide(imagem.select('SR_B3').add(imagem.select('SR_B5')))
      .rename('NDWI');

    map.addLayer(ndwi, {min: -1, max: 1, palette: ['red', 'white', 'blue']}, 'NDWI');
    map.addLayer(mndwi, {min: -1, max: 1, palette: ['red', 'white', 'blue']}, 'MNDWI');
    map.addLayer(rwi, {min: -1, max: 1, palette: ['red', 'white', 'blue']}, 'RWI');
  });
}

// 5. Areas FeatureCollection
var area = ee.FeatureCollection('projects/ee-efjustiniano/assets/doutorado/waterIndex/areasIndex');

var areaNames = area.aggregate_array("area").distinct().sort();

// Panels
areaNames.evaluate(function(names) {

var SelectDropdown = ui.Select({
  items: names,
  placeholder: 'Selecione a área',
  onChange: function(areaName) {
    showArea(areaName);
  }
});
  // Lateral panel
  var sidePanel = ui.Panel({style: {width: '170px'}});
  sidePanel.add(ui.Label('Select area', {fontWeight: 'bold', fontSize: '14px'}));
  sidePanel.add(SelectDropdown);

  // Credits
  var expl = ui.Label('Landsat-8 and Landsat-9; 2023 image collection; RWI, MNDWI, and NDWI (ajusted values between -1 and +1)', {fontSize: '12px', textAlign: 'center'});
  var logoImage = ee.Image('projects/ee-efjustiniano/assets/doutorado/vlogos')
    .visualize({bands: ['b1', 'b2', 'b3'], min: 0, max: 255});
  var logoThumb = ui.Thumbnail({image: logoImage, params: {dimensions: '964x2851'}, style: {width: '144px'}});
  var linha = ui.Label('___________', {textAlign: 'center'});
  var cred1 = ui.Label('Dr. Eduardo Felix Justiniano', {textAlign: 'center'});
  var cred2 = ui.Label('Prof. Dr. Fernando Shingi Kawakubo', {textAlign: 'center'});

  var IEEE = ui.Label({
    value: '🔗 Rescaled Water Index',
    style: {fontSize: '10px', color: '#1155cc', textAlign: 'center'},
    targetUrl: 'https://doi.org/10.1109/JSTARS.2025.3562089'
  });

  var painelLogo = ui.Panel([expl, IEEE, linha, cred1, cred2, logoThumb], ui.Panel.Layout.flow('vertical'));

  sidePanel.add(painelLogo);

  // Main panel
  var painelPrincipal = ui.Panel({
    layout: ui.Panel.Layout.flow('horizontal'),
    style: {stretch: 'both'}
  });

  painelPrincipal.add(sidePanel);
  painelPrincipal.add(map);

  ui.root.clear();
  ui.root.add(painelPrincipal);
  map.setControlVisibility({ searchControl: false });
});
