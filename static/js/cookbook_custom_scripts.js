// #region AJAX send the signup data to Flask/Python

$(function () {
  $('#signupForm').submit(function (event) {
    event.preventDefault();
    $.ajax({
      url: '/signup_user',
      data: $('#signupForm').serialize(),
      type: 'POST',
      success: function (response) {
        console.log(response);
        if (response == "success") {
          var message = "Success. Log in now."
          $("#signupMessages").html(message);
          var delay = 1000;
          setTimeout(function () { window.location.href = "/"; }, delay);
        }
        else if (response == "fail") {
          var message = "Failure name take"
          $("#signupMessages").html(message);
        }
      },
      error: function (error) {
        console.log(error);
        $("#signupMessages").html(response);
      }
    });
  });
});

// #endregion


// #region AJAX send the login data to Flask/Python

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

// #endregion


// #region AJAX send the new recipe data from form to Flask/Python

$(function () {
  $('#add_recipe_form').submit(function (event) {
    event.preventDefault();
    $.ajax({
      url: '/insert_recipe',
      data: $('#add_recipe_form').serialize(),
      type: 'POST',
      success: function (response) {
        console.log("RESPONSE FROM SERVER", response);
        $("#newRecipeMessages").html(response);
        // Delay before redirect to read message
        var delay = 1200;
        setTimeout(function () { window.location.href = "/profile"; }, delay);
      },
      error: function (error) {
        console.log(error);
        $("#newRecipeMessages").html(response);
      }
    });
  });
});

// #endregion


// #region AJAX update a recipe send data from form to server

$(function () {
  $('#update_recipe_form').submit(function (event) {
    event.preventDefault();
    var url = window.location.href;
    recipe_id = url.split("/").pop();
    $.ajax({
      url: '/update_recipe/' + recipe_id,
      data: $('#update_recipe_form').serialize(),
      type: 'POST',
      success: function (response) {
        console.log("RESPONSE FROM SERVER", response);
        $("#editRecipeMessages").html(response);
        window.location.href = "/profile";
        // Delay before redirect to read message
        // var delay = 1200;
        // setTimeout(function () { window.location.href = "/profile"; }, delay);
      },
      error: function (error) {
        console.log(error);
        $("#editRecipeMessages").html(response);
      }
    });
  });
});

// #endregion


// #region show/hide the Debug Panel
function viewPanel() {
  var panel = document.getElementById("panel-debug");
  if (panel.style.display === "none") {
    panel.style.display = "block";
  }
  else {
    panel.style.display = "none";
  }
}

// #endregion


// #region GO BACK TO PREVIOUS PAGE

function goPrev() {
  window.history.back();
}

// #endregion


// #region DOCUMENT.READY START //

$(document).ready(function () {

  // #region Add class to navbar link depending on the page displayed  

  var current_path = $(location).attr('pathname');
  if (current_path == "/profile") {
    $("#profile-nav-link").addClass("active-link");
  }
  else if (current_path == "/add_recipe") {
    $("#add-nav-link").addClass("active-link");
  }

  // #endregion

    // #region Add class welcome user message if home page  

    var current_path = $(location).attr('pathname');
    if (current_path == "/") {
      $(".userwelcome").addClass("home-userwelcome");
    }
  
    // #endregion 


  // #region Add extra ingredient or instruction inputs to add recipe form

  $('#add_ingredient').click(function () {
    addExtraInputs("i");
    return false; //return false;  stops page jumping back to top
  })

  $('#add_instruction').click(function () {
    addExtraInputs("m");
    return false; //return false;  stops page jumping back to top
  })

  function addExtraInputs(inputs) {
    if (inputs == "i") {
      var ingred = '<div class="added-ingred">' +
        '<input type="text" class="input form-control" placeholder="ingredient" name="ingredient">' +
        '<a href="#"><i class="fa fa-minus-circle delete" aria-hidden="true"></i></a></div>';
      $("#ingredients_input_list").append(ingred);
    }
    else {
      var method = '<div class="added-instruction">' +
        '<textarea class="input form-control" placeholder="instruction" name="instruction"></textarea>' +
        '<a href="#"><i class="fa fa-minus-circle delete" aria-hidden="true"></i></a></div>';
      $("#instruction_input_list").append(method);
    }
  }

  $(function () {
    $('#ingredients_input_list').on('click', '.delete', function () {
      var rem = $(this).closest('div.added-ingred');
      $(rem).remove();
      return false; //return false;  stops page jumping to top
    });
  });

  $(function () {
    $('#instruction_input_list').on('click', '.delete', function () {
      var rem = $(this).closest('div.added-instruction');
      $(rem).remove();
      return false; //return false;  stops page jumping to top
    });
  });

  // #endregion


  // #region CONFIRM WITH USER BEFORE DELETING A RECIPE

  $(function () {
    $('.delete_recipe').click(function (e) {
      e.preventDefault();
      // GET THE ID OF THE RECIPE APPENDED TO DELETE BUTTON ID
      var thisrecipeid = this.id;
      $("#confirm_delete").dialog({
        hide: { effect: "explode", duration: 1000 },
        "ui-dialog": "ui-corner-all",
        "ui-dialog-titlebar": "ui-corner-all",
        dialogClass: "alert",
        resizable: false,
        height: 330,
        width: 500,
        modal: true,
        buttons: {
          "Delete all items": function () {
            $(this).dialog("close");
            var recipe_id = thisrecipeid
            $.ajax({
              url: '/delete_recipe',
              data: { "recipe_id": recipe_id },
              type: 'POST',
              success: function (response) {
                console.log("RESPONSE FROM SERVER", response);
                $("#profileMessages").html(response);
                window.location.href = "/profile";
              },
              error: function (error) {
                console.log(error);
                $("#profileMessages").html(response);
              }
            });
          },
          Cancel: function () {
            $(this).dialog("close");
          }
        }
      });
      return false;
    });
  });

  // #endregion


  // #region View Recipe page change from flat content to tabs in mobile view

  $(window).on('resize', function () {
    var win = $(this); //this = window
    if (win.width() >= 768) {
      $("#home").css("display", "block");
      $("#profile").css("display", "block");
    }
    else if (win.width() <= 767) {
      if ($("#hometab>a").is(".active")) {
        $("#home").css("display", "block");
        $("#profile").css("display", "none");
      }
      else if ($("#ptab>a").is(".active")) {
        $("#home").css("display", "none");
        $("#profile").css("display", "block");
      }
    }
  });

  $('#hometab').click(function () {
    $("#home").css("display", "block");
    $("#profile").css("display", "none");
  })
  $('#ptab').click(function () {
    $("#profile").css("display", "block");
    $("#home").css("display", "none");
  })

  // #endregion

  
  // #region RATE THIS RECIPE

  $('#rateme').click(function (e) {
    e.preventDefault();
    addVote();
    return false; //return false;  stops page jumping back to top
  })

  function addVote() {
    votes = 1;
    var url = window.location.href;
    recipe_id = url.split("/").pop();
    console.log("got to here", votes)
    $.ajax({
      url: '/update_vote/' + recipe_id,
      contentType: 'application/json',
      data: JSON.stringify(votes),
      type: 'POST',
      success: function (response) {
        console.log("RESPONSE FROM SERVER", response);
        $("#ratemeMessages").html(response);
        $("#vote_result").html(response);
      },
      error: function (error) {
        console.log(error);
        $("#ratemeMessages").html(response);
      }
    });
  };
  // #endregion


  // #region GET CATEGORY FROM SEARCH FILTER AND PASS TO FLASK

  $(function () {
    $("#category-select").change(function (event) {
      event.preventDefault();
      var categorypicked = $('#category-select').find(":selected").text();
      $("#sc").text(categorypicked);
      category = categorypicked.trim();
      console.log("category selected:", category)
      $.ajax({
        url: '/filter_by_category/'+ category,
        contentType: 'application/json',
        data: JSON.stringify(category),
        type: 'POST',
        success: function (response) {
          console.log("RESPONSE FROM SERVER", response);
          // $.each(response, function(k, v) {
          //   console.log(response)
          // });
          // parsedResponse = JSON.parse(response)
          // console.log(parsedResponse)
          // $.each(parsedResponse, function() {
          //   $.each(this, function(k, v) {
          //     console.log(k, v)
          //     $("#recipeResult").html(k,v);
          //     $('#initialRecipes').hide();
          //   });
          // });
          $("#recipeResult").html(response);
          // $("#one").html(response.description);
          // $("#two").html("shit");
          // $("#recipeResult>#thisisacol>.recipe-name").html(response.cuisine);
          $('#initialRecipes').hide();
        },
        error: function (error) {
          console.log(error);
          $("#recipeResult").html(response);
        }
      });
    });
});

// #endregion


  // #region GET CUISINE FROM SEARCH FILTER AND PASS TO FLASK

 $(function () {
  $("#cuisine-select").change(function (event) {
    event.preventDefault();
    var cuisinepicked = $('#cuisine-select').find(":selected").text();
    $("#sc").text(cuisinepicked);
    cuisine = cuisinepicked.trim();
    console.log("cuisine selected:", cuisine)
    $.ajax({
      url: '/filter_by_cuisine/'+ cuisine,
      contentType: 'application/json',
      data: JSON.stringify(cuisine),
      type: 'POST',
      success: function (response) {
        console.log("RESPONSE FROM SERVER", response);
        $("#recipeResult").html(response);
        $('#initialRecipes').hide();
      },
      error: function (error) {
        console.log(error);
        $("#recipeResult").html(response);
      }
    });
  });
});

// #endregion


  // #region GET ALLERGENS FROM SEARCH FILTER AND PASS TO FLASK

 $(function () {
  $("#allergen-select").change(function (event) {
    event.preventDefault();
    var allergenpicked = $('#allergen-select').find(":selected").text();
    allergen = allergenpicked.trim();
    console.log("allergen selected:", allergen)
    $.ajax({
      url: '/filter_by_allergen/'+ allergen,
      contentType: 'application/json',
      data: JSON.stringify(allergen),
      type: 'POST',
      success: function (response) {
        console.log("RESPONSE FROM SERVER", response);
        $("#recipeResult").html(response);
        $('#initialRecipes').hide();
      },
      error: function (error) {
        console.log(error);
        $("#recipeResult").html(response);
      }
    });
  });
});

// #endregion



}); // close document.ready
// #endregion

