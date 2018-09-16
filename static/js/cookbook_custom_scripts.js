//AJAX send the signup data to the back end

$(function () {
  $('#signupForm').submit(function (event) {
    event.preventDefault();
    $.ajax({
      url: '/signup_user',
      data: $('#signupForm').serialize(),
      type: 'POST',
      success: function (response) {
        console.log(response);
        $("#signupMessages").html(response);
        var delay = 1000;
        setTimeout(function () { window.location.href = "/"; }, delay);
      },
      error: function (error) {
        console.log(error);
        $("#signupMessages").html(response);
      }
    });
  });
});


//AJAX send the login data to the back end

$(function () {
  $('#loginForm').submit(function (event) {
    event.preventDefault();
    $.ajax({
      url: '/login_user',
      data: $('#loginForm').serialize(),
      type: 'POST',
      success: function (response) {
        console.log(response);
        $("#loginMessages").html(response.message);
        //Add username and id to localstorage        
        localStorage.setItem("username", response.username);
        localStorage.setItem("user_id", response._id);
        // Delay before redirect to read message
        var delay = 1200;
        setTimeout(function () { window.location.href = "/profile"; }, delay);
      },
      error: function (error) {
        console.log(error);
        $("#loginMessages").html(response);
      }
    });
  });
});


// show/hide the Debug Panel
function viewPanel() {
  var panel = document.getElementById("panel-debug");
  if (panel.style.display === "none") {
    panel.style.display = "block";
  }
  else {
    panel.style.display = "none";
  }
}

// add class to navbar link depending on the page displayed
$(document).ready(function () {
  var current_path = $(location).attr('pathname');
  //console.log(current_path)
  if (current_path == "/profile") {
    $("#profile-nav-link").addClass("active-link");
  }
  else if (current_path == "/add_recipe") {
    $("#add-nav-link").addClass("active-link");
  }

  // add ingredients to add recipe form
  // var max_fields = 6; 
  // var x = 1; 
  // $("#add_ingredient").on("click", function (e) {
  //     e.preventDefault();
  //     if (x < max_fields) { 
  //         x++; 
  //         $('#ingredients_input_list').append("<div>" +
  //         "<input type='text' class='form-control' id='ingredients" + x + "'name='ingredients'" + x + ">" +
  //         "<a href='' class='remove_ingredient_input' id='woo'>" +
  //         "<i class='fa fa-minus-circle' aria-hidden='true'></i>" +
  //         "</a>" + 
  //         x + 
  //         "</div>");
  //     }
  // });        
  // $('#add_recipe_form').on('click', '.remove_ingredient_input', function () { 
  //     $(this).parent().remove();
  //     x--;
  // })


  var next = 1;
  $("#add_ingredient").click(function (e) {
    e.preventDefault();
    var max_fields = 6;
    var addto = "#ingredient" + next;
    var addRemove = "#ingredient" + (next);
    next = next + 1;
    // if (next < max_fields) {
      var newIn = '<input class="input form-control" id="ingredient' + next + '" name="ingredient' + next + '" type="text" placeholder="ingredient ' + next + '">';
      var newInput = $(newIn);
      var removeBtn = '<a href="#" id="remove' + (next - 1) + '" class="remove-me"><i class="fa fa-minus-circle" aria-hidden="true"></i></a>';
      var removeButton = $(removeBtn);
      $(addto).after(newInput);
      $(addRemove).after(removeButton);
      $("#ingredient" + next).attr('data-source', $(addto).attr('data-source'));
      $("#count").val(next);
    // }
    

    $('.remove-me').click(function (e) {
      e.preventDefault();
      var fieldNum = this.id.charAt(this.id.length - 1);
      var fieldID = "#ingredient" + fieldNum;
      $(this).remove();
      $(fieldID).remove();
    });
  });

});

