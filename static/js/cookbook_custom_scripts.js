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


//AJAX send the new recipe data from form to server

$(function () {
  $('#add_recipe_form').submit(function (event) {
    event.preventDefault();
    var user_id = localStorage.getItem("user_id");
    var form_data = $('#add_recipe_form').serialize()
    console.log("FORM ID", user_id)
    console.log("FORM DATA", form_data)
    $.ajax({
      url: '/insert_recipe',
      data: $('#add_recipe_form').serialize(),
      type: 'POST',
      success: function (response) {
        console.log("RESPONSE FROM SERVER", response);
        $("#newRecipeMessages").html(response);
        // Delay before redirect to read message
        // var delay = 1200;
        // setTimeout(function () { window.location.href = "/profile"; }, delay);
      },
      error: function (error) {
        console.log(error);
        $("#newRecipeMessages").html(response);
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

  //get localstorage user_id and set hidden field in add recipe form
  var user_id = localStorage.getItem("user_id");
  //console.log(user_id);
  document.getElementById("form_user_id").value = user_id;
  }




  // add extra ingredient or instruction inputs to add recipe form
  $('#add_ingredient').click(function () {
    addExtraInputs("i");
  })

  $('#add_method').click(function () {
    addExtraInputs("m");
  })

  function addExtraInputs(inputs) {
    if (inputs == "i") {
      var ingred = '<div class="added-ingred">' +
        '<input type="text" class="input form-control" placeholder="ingredient">' +
        '<a href="#"><i class="fa fa-minus-circle delete" aria-hidden="true"></i></a></div>';
      $("#ingredients_input_list").append(ingred);
    }
    else {
      var method = '<div class="added-method">' +
        '<textarea class="input form-control" placeholder="intructions"></textarea>' +
        '<a href="#"><i class="fa fa-minus-circle delete" aria-hidden="true"></i></a></div>';
      $("#method_input_list").append(method);
    }
  }

  $(function () {
    $('#ingredients_input_list').on('click', '.delete', function () {
      var rem = $(this).closest('div.added-ingred');
      $(rem).remove();
    });
  });

  $(function () {
    $('#method_input_list').on('click', '.delete', function () {
      var rem = $(this).closest('div.added-method');
      $(rem).remove();
    });
  });

  $('.submit-btn').click(function () {
    $('.ingredients-list  > input').each(function () {
      // console.log($(this).text());
      console.log($(this).val());
    });
  })

});

