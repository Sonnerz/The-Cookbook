// #region AJAX send the SIGNUP data to Flask/Python

$(function () {
  $('#signupForm').submit(function (event) {
    event.preventDefault();
    // ensure passwords match
    if ($('#signupPassword').val() == $('#confirmPassword').val()) {
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
    } else
      $('#signupMessages').html('Passwords do not match').css('color', 'red');
  });
});

// #endregion


// #region AJAX send the LOGIN data to Flask/Python

$(function () {
  $('#loginForm').submit(function (event) {
    event.preventDefault();
    $.ajax({
      url: '/login_user',
      data: $('#loginForm').serialize(),
      type: 'POST',
      success: function (response) {
        console.log(response);
        if (response == 1) {
          $("#loginMessages").html("The password was incorrect");
        }
        else if (response == 2) {
          $("#loginMessages").html("That username is not registered");
        }
        else {
          $("#loginMessages").html(response.message);
          //Add username and id to localstorage        
          localStorage.setItem("username", response.username);
          localStorage.setItem("user_id", response._id);
          // Delay before redirect to myrecipes page
          var delay = 1200;
          setTimeout(function () { window.location.href = "/myrecipes?limit=5&offset=0"; }, delay);
        }
      },
      error: function (error) {
        console.log(error);
        $("#loginMessages").html(response);
      }
    });
  });
});

// #endregion


// #region AJAX send the NEW RECIPE data from form to Flask/Python

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
        setTimeout(function () { window.location.href = "/myrecipes"; }, delay);
      },
      error: function (error) {
        console.log(error);
        $("#newRecipeMessages").html(response);
      }
    });
  });
});

// #endregion


// #region AJAX UPDATEA RECIPE send data from form to server

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
        window.location.href = "/myrecipes?limit=5&offset=0";
        // Delay before redirect to read message
        // var delay = 1200;
        // setTimeout(function () { window.location.href = "/myrecipes"; }, delay);
      },
      error: function (error) {
        console.log(error);
        $("#editRecipeMessages").html(response);
      }
    });
  });
});

// #endregion


// #region show/hide the DEBUG PANEL
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
  //hide search results div until populated with data
  $("#searchResult").hide();


  // #region Add class to NAVBAR LINK depending on the page displayed  

  var current_path = $(location).attr('pathname');
  if (current_path == "/myrecipes") {
    $("#myrecipes-nav-link").addClass("active-link");
  }
  else if (current_path == "/add_recipe") {
    $("#add-nav-link").addClass("active-link");
  }
  else if (current_path == "/recipesearch") {
    $("#search-nav-link").addClass("active-link");
  }

  // #endregion


  // #region Add class WELCOME USER MESSAGE if home page  

  var current_path = $(location).attr('pathname');
  if (current_path == "/") {
    $(".userwelcome").addClass("home-userwelcome");
  }

  // #endregion 


  // #region Add EXTRA INGREDIENT OR INSTRUCTION inputs to add recipe form

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
                $("#myrecipesMessages").html(response);
                window.location.href = "/myrecipes";
              },
              error: function (error) {
                console.log(error);
                $("#myrecipesMessages").html(response);
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


  // #region VIEW RECIPE page change from FLAT CONTENT TO TABS in mobile view

  $(window).on('resize', function () {
    var win = $(this); //this = window
    if (win.width() >= 768) {
      $("#home").css("display", "block");
      $("#myrecipes").css("display", "block");
    }
    else if (win.width() <= 767) {
      if ($("#hometab>a").is(".active")) {
        $("#home").css("display", "block");
        $("#myrecipes").css("display", "none");
      }
      else if ($("#ptab>a").is(".active")) {
        $("#home").css("display", "none");
        $("#myrecipes").css("display", "block");
      }
    }
  });

  $('#hometab').click(function () {
    $("#home").css("display", "block");
    $("#myrecipes").css("display", "none");
  })
  $('#ptab').click(function () {
    $("#myrecipes").css("display", "block");
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
      category = categorypicked.trim();
      console.log("category selected:", category)
      $.ajax({
        url: '/filter_by_category/' + category,
        contentType: 'application/json',
        data: JSON.stringify(category),
        type: 'POST',
        success: function (response) {
          console.log("RESPONSE FROM SERVER", response);
          $("#searchResult").show();
          $("#recipeResult").html(response);
          $("h3").html("Recipes searched by Category: " + categorypicked)
          // $('#cuisine-select').val("Select a Cuisine");
          // $('#allergen-select').val("Select an Allergen");
          $('.initialRecipes').hide();
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
        url: '/filter_by_cuisine/' + cuisine,
        contentType: 'application/json',
        data: JSON.stringify(cuisine),
        type: 'POST',
        success: function (response) {
          console.log("RESPONSE FROM SERVER", response);
          $("#searchResult").show();
          $("h3").html("Recipes searched by Cuisine: " + cuisinepicked)
          // $('#category-select').val("Select a Category");
          // $('#allergen-select').val("Select an Allergen");
          $("#recipeResult").html(response);
          $('.initialRecipes').hide();
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
        url: '/filter_by_allergen/' + allergen,
        contentType: 'application/json',
        data: JSON.stringify(allergen),
        type: 'POST',
        success: function (response) {
          console.log("RESPONSE FROM SERVER", response);
          $("#searchResult").show();
          $("h3").html("Recipes searched by Allergen: " + allergenpicked)
          // $('#category-select').val("Select a Category");
          // $('#cuisine-select').val("Select a Cuisine");
          $("#recipeResult").html(response);
          $('.initialRecipes').hide();
        },
        error: function (error) {
          console.log(error);
          $("#recipeResult").html(response);
        }
      });
    });
  });

  // #endregion


  // #region GET INGREDIENT FROM SEARCH FILTER AND PASS TO FLASK

  $(function () {
    $('#ingredientFilter').submit(function (event) {
      event.preventDefault();
      var ingredient = $('#searchmain').val()
      console.log(ingredient)
      $.ajax({
        url: '/filter_by_ingredient',
        data: ingredient,
        type: 'POST',
        success: function (response) {
          console.log("RESPONSE FROM SERVER", response);
          $("#searchResult").show();
          $("h3").html("Recipes searched by Ingredient: ")
          $("#recipeResult").html(response);
          $('.initialRecipes').hide();
        },
        error: function (error) {
          console.log(error);
          $("#recipeResult").html(response);
        }
      });
    });
  });

  // #endregion


  // #region GET CATEGORY & CUISINE FROM SEARCH FILTER AND PASS TO FLASK

  $(function () {
    $('#categorycuisineFilter').submit(function (event) {
      event.preventDefault();
      var cuisinepicked = $('#cuisine-select1').find(":selected").text();
      var categorypicked = $('#category-select1').find(":selected").text();
      cuisine = cuisinepicked.trim();
      category = categorypicked.trim();
      console.log(cuisine, category)
      console.log("cuisine selected:", cuisine);
      $.ajax({
        url: '/filter_by_catcuis/' + category + '/' + cuisine,
        contentType: 'application/json',
        data: JSON.stringify(cuisine),
        type: 'POST',
        success: function (response) {
          console.log("RESPONSE FROM SERVER", response);
          $("#searchResult").show();
          $("h3").html("Recipes searched by Category: " + cuisinepicked + " and Category: " + categorypicked);
          // $('#category-select').val("Select a Category");
          // $('#allergen-select').val("Select an Allergen");
          $("#recipeResult").html(response);
          $('.initialRecipes').hide();
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

