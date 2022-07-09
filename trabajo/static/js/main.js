//append  skill
let index = $('.userskill').length + 1

$('#addSkill').click(function(){
    let input = '<div id="fieldremove'+index+'" class=""><input class="form-control skillinput" type="text" name="skill[]" placeholder="Add skill"><i id="'+index+'" class="remove bi bi-x-octagon skillremove"></i></div>';
    $('#appendField').append(input);
    index++;
});

$(document).on('click', '.remove', function(){
    let ids = $(this).attr("id");
    $('#fieldremove'+ids+'').remove();
});

$(document).ready(function(){
$('[data-toggle="tooltip"]').tooltip();
});

// image upload
$("#submitForm").on("change", function(){
    let formData = new FormData(this);
    $.ajax({
        url  : "/profile_image",
        type : "POST",
        cache: false,
        contentType : false,
        processData: false,
        data: formData,
        success:function(response){
        location.reload();
        console.log("uploaded Successfully");
        }
    });
});


function uploadFiles() {
    let file = document.getElementById('file_upload');
    if(file.length==0){
      alert("Please first choose or drop a file...");
      return;
    }
  }

  var wtf_phone_field = document.getElementById('phone_number');
  wtf_phone_field.style.position = 'absolute';
  wtf_phone_field.style.top = '-9999px';
  wtf_phone_field.style.left = '-9960px';
  wtf_phone_field.parentElement.insertAdjacentHTML('beforeend', '<div><input type="tel" id="_phone" class="form-control"></div>');
  var fancy_phone_field = document.getElementById('_phone');
  var fancy_phone_iti = window.intlTelInput(fancy_phone_field, {
      separateDialCode: true,
      utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/16.0.4/js/utils.js",
  });
  fancy_phone_iti.setNumber(wtf_phone_field.value);
  fancy_phone_field.addEventListener('blur', function() {
      wtf_phone_field.value = fancy_phone_iti.getNumber();
  });