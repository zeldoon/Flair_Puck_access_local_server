var irCodesHash = '';

function timeStampFormatter(value) {
  return (new Date(value*1000)).toLocaleString();
}

function checkBoxFormatter(value) {
  return '<input uuid="' + value + '" type="checkbox">'
}

function hvacDeviceCommandMetaDataForm(value) {

  return '<label>Device Make<input class="device_make" type="textbox" value="' + value['device_make'] + '"></label>' +
         '<label>Device Model<input class="device_model" type="textbox" value="' + value['device_model'] + '"></label>' +
         '<label>Remote Make<input class="remote_make" type="textbox" value="' + value['remote_make'] + '"></label>' +
         '<label>Remote Model<input class="remote_model" type="textbox" value="' + value['remote_model'] + '"></label>' +
         '<label>Power<input class="power_state" type="textbox" value="' + value['power_state'] + '"></label>' +
         '<label>Fan<input class="fan_state" type="textbox" value="' + value['fan_state'] + '"></label>' +
         '<label>Temperature<input class="temperature_state" type="textbox" value="' + value['temperature_state'] + '"></label>' +
         '<label>Mode<input class="mode_state" type="textbox" value="' + value['mode_state'] + '"></label>' +
         '<label>Swing<input class="swing_state" type="textbox" value="' + value['swing_state'] + '"></label>';
}

function AVDeviceCommandMetaDataForm(value) {

  return '<label>Command Name<input class="command_name" type="textbox" value="' + value['command_name'] + '"></label>' +
         '<label>Device Make<input class="device_make" type="textbox" value="' + value['device_make'] + '"></label>' +
         '<label>Device Model<input class="device_model" type="textbox" value="' + value['device_model'] + '"></label>' +
         '<label>Remote Make<input class="remote_make" type="textbox" value="' + value['device_model'] + '"></label>' +
         '<label>Remote Model<input class="remote_model" type="textbox" value="' + value['remote_model'] + '"></label>';
}

function metaDataForm(value) {
  return '<div class="command-metadata-form-container">'
          + '<ul class="nav nav-tabs">'
          + '<li id="hvac-metadata-form-tab-'+ value['uuid'] + '" class="active hvac-metadata-form-tab"><a href="#" onclick="showHVACFormHideAVForm(\'' + value['uuid'] + '\');">HVAC</a></li>'
          + '<li id="av-metadata-form-tab-'+ value['uuid'] + '"class="av-metadata-form-tab"><a href="#" onclick="showAVFormHideHVACForm(\'' + value['uuid'] + '\');">AV</a></li>'
          + '</ul>'
          + '<div id="hvac-metadata-form-'+ value['uuid'] +'" class="hvac-metadata-form">'
          + hvacDeviceCommandMetaDataForm(value)
          + '</div>'
          + '<div id="av-metadata-form-'+ value['uuid'] +'" class="av-metadata-form" style="display: none;">'
          + AVDeviceCommandMetaDataForm(value)
          + '</div></div>';
}

function checkForIRChangesAndUpdate() {
  $.get( "/ir_codes/hash", function( data ) {
    if (irCodesHash != data) {
      updateTable();
    }
    irCodesHash = data;
    setTimeout(checkForIRChangesAndUpdate, 1000);
  });
}

function showHVACFormHideAVForm(uuid) {
  $('#hvac-metadata-form-' + uuid).show();
  $('#hvac-metadata-form-tab-' + uuid).addClass('active');
  $('#av-metadata-form-'+ uuid).hide();
  $('#av-metadata-form-tab-' + uuid).removeClass('active');
}

function showAVFormHideHVACForm(uuid) {
    $('#hvac-metadata-form-'+ uuid).hide();
    $('#hvac-metadata-form-tab-' + uuid).removeClass('active');
    $('#av-metadata-form-'+ uuid).show();
    $('#av-metadata-form-tab-' + uuid).addClass('active');
}


function updateTable() {
  $('.table').bootstrapTable('refresh', {silent: true});
}

function getHVACDeviceMetaData(uuid) {
  var form = $('#hvac-metadata-form-' + uuid);
  var response = {
    device_make: form.find('.device_make').val(),
    device_model: form.find('.device_model').val(),
    remote_make: form.find('.remote_make').val(),
    remote_model: form.find('.remote_model').val(),
    power_state: form.find('.power_state').val(),
    fan_state: form.find('.fan_state').val(),
    temperature_state: form.find('.temperature_state').val(),
    mode_state: form.find('.mode_state').val(),
    swing_state: form.find('.swing_state').val()
  };
  var empty = true;
  Object.keys(response).forEach(function(key) {
    if (response[key] != '') {
      return false;
    }
  });
  return response;
}

function getAVDeviceMetaData(uuid) {
  var form = $('#av-metadata-form-' + uuid);
  var response = {
    command_name: form.find('.command_name').val(),
    device_make: form.find('.device_make').val(),
    device_model: form.find('.device_model').val(),
    remote_make: form.find('.remote_make').val(),
    remote_model: form.find('.remote_model').val()
  };
  var empty = true;
  Object.keys(response).forEach(function(key) {
    if (response[key] != '') {
      return false;
    }
  });
  return response;
}

function getMetaData(uuid) {
    var hvacDeviceMetaData = getHVACDeviceMetaData(uuid);
    var avDeviceMetaData = getAVDeviceMetaData(uuid);
    console.log(avDeviceMetaData);
    if (!hvacDeviceMetaData && !avDeviceMetaData) {
      return false;
    } else if (hvacDeviceMetaData) {
      return hvacDeviceMetaData;
    }
    return avDeviceMetaData;
}

checkForIRChangesAndUpdate();

$(document).ready(function() {

  $('#remove-codes').click(function() {
    //lookup each checked box and delete them
    var uuidsToDelete = $( "input:checked" ).map(function(){return $(this).attr("uuid");}).get();

    for (var i = 0; i < uuidsToDelete.length; i++) {
      $.ajax({
        url: '/ir_codes/' + uuidsToDelete[i],
        type: 'DELETE',
        success: function(result) {
          updateTable();
        }
      });
    };
  });

  $('#save-metadata').click(function(event) {
    event.preventDefault();
    var uuids = $( "input:checked" ).map(function(){return $(this).attr("uuid");}).get();
    if (!uuids.length) {
      alert('select commands to save');
    }
    // Should probably have a warning that lets you cancel so you don't wipe out a bunch of meta data
    for (var i = 0; i < uuids.length; i++) {
      var metadata = getMetaData(uuids[i]);
      if (metadata) {
        $.ajax({
          url: '/ir_codes/' + uuids[i],
          type: 'PATCH',
          data: JSON.stringify(metadata),
          contentType: "application/json",
          success: function(result) {
            updateTable();
          }
        });
      } else {
        alert('failed to upload all codes due to hvac/av ambiguity');
      }
    };
  });

  $('#checkbox-all').click(function() {
      if(this.checked) {
        $("input:checkbox").prop('checked',this.checked);
      } else {
        $('input:checkbox').prop('checked', false);
      }
  });

  // no matter what can't get this to bind so adding onclick to the elements to move on...
  // $('.table').bootstrapTable({
  //   onAll: function() {
  //     alert('refresh finished');
  //
  //     // for row in table
  //     // if av meta data is not empty, show avform
  //
  //     //bind table event handlers here
  //     $('.hvac-metadata-form-tab').click(function(e) {
  //       e.preventDefault();
  //       alert('1');
  //       showHVACFormHideAVForm(this);
  //     });
  //
  //     $('.av-metadata-form-tab').click(function(e) {
  //       e.preventDefault();
  //       alert('2');
  //       showAVFormHideHVACForm(this);
  //     });
  //   }
  // });
});
