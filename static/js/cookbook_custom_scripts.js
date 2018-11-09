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
          if (response == "success") {
            var message = "Your account was created. You can log in now.";
            $("#signupMessages").html(message);
            var delay = 1000;
            setTimeout(function () { window.location.href = "/"; }, delay);
          }
          else if (response == "fail") {
            var messagefail = "This username has already been registered.";
            $("#signupMessages").html(messagefail);
          }
        },
        error: function (error) {
          $("#signupMessages").html("There was an error creating your account. Please try again.");
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
        $("#loginMessages").html("There was an error logging in. Please try again");
      }
    });
  });
});

// #endregion


// #region AJAX ADD NEW RECIPE

$(function () {
  $('#add_recipe_form').submit(function (event) {
    event.preventDefault();
    //scroll window to results
    $('html, body').animate({
      scrollTop: $("#page-top").offset().top -300
    }, 'slow');    
    var categorypicked = $('#category').find(":selected").text();
    var cuisinepicked = $('#cuisine').find(":selected").text();
    var difficultypicked = $('#difficulty').find(":selected").text();
    if (categorypicked == "Select a Category" || cuisinepicked == "Select a Cuisine" || difficultypicked == "Select a Difficulty level") {
      $("#newRecipeMessages").html("You must select a Category, Cuisine and Difficulty Level");
    }
    else {
      $.ajax({
        url: '/insert_recipe',
        data: $('#add_recipe_form').serialize(),
        type: 'POST',
        success: function (response) {
          $("#newRecipeMessages").html(response);
          $("h3.section-subheading").html("Your recipe has been added");
          // Delay before redirect to myrecipes
          var delay = 1200;
          setTimeout(function () { window.location.href = "/myrecipes?limit=5&offset=0"; }, delay);
        },
        error: function (error) {
          $("#newRecipeMessages").html("There was an error adding your recipe. Please try again.");
        }
      });
    }
  });
});

// #endregion


// #region AJAX UPDATE A RECIPE

$(function () {
  $('#update_recipe_form').submit(function (event) {
    event.preventDefault();
    var url = window.location.href;
    var recipe_id = url.split("/").pop();
    $.ajax({
      url: '/update_recipe/' + recipe_id,
      data: $('#update_recipe_form').serialize(),
      type: 'POST',
      success: function (response) {
        $("#editRecipeMessages").html(response);
        window.location.href = "/myrecipes?limit=5&offset=0";
      },
      error: function (error) {
        $("#editRecipeMessages").html("There was an error updating your recipe. Please try again.");
      }
    });
  });
});

// #endregion


// #region GO BACK TO PREVIOUS PAGE

function goPrev() {
  window.history.back();
}

// #endregion


// #region SCROLL BACK TO TOP OF PAGE

// https://www.w3schools.com/howto/howto_js_scroll_to_top.asp
// When the user scrolls down 20px from the top of the document, show the button

window.onscroll = function() {scrollFunction()};

function scrollFunction() {
    if (document.body.scrollTop> 20 || document.documentElement.scrollTop > 20) {
        document.getElementById("backtotopIcon").style.display = "block";
    } else {
        document.getElementById("backtotopIcon").style.display = "none";
    }
}

// When the user clicks on the button, scroll to the top of the document
function topFunction() {
    document.body.scrollTop = 0; // For Safari
    // document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
    $('html, body').animate({
      scrollTop: $("#page-top").offset().top -50
    }, 'slow');
}
// #endregion


// #region SEARCH ANY FIELD RECIPE HASHTAGS

function searchdb(a){
  var searchQuery = a.innerHTML;
  $.ajax({
    url: '/recipesearchquery',
    contentType: 'application/json',
    data: JSON.stringify(searchQuery),
    type: 'POST',
    success: function (response) {
      $('.initialRecipes').hide();
      $("#searchResult").show();
      $("h3.section-subheading").html("Recipes searched by Ingredient: " + searchQuery);
      if (response != "fail") {
        $("#recipeResult").html(response);
      }
      else {
        $("#recipeResult").html("There were no recipes found with <span class='search-param'>" + searchQuery + "</span> as a search value. <br>Try searching again." );
      }
      //scroll window to results
      $('html, body').animate({
        scrollTop: $(".results-col").offset().top -300
      }, 'slow');
    },
    error: function (error) {
      $("#recipeResult").html("There was an error completing your search.");
    }
  });
}
// #endregion


// #region MOBILE TABS SHOW/HIDE CONTENT
// Inspired by code on StackOverflow:
// https://stackoverflow.com/questions/23555978/bootstrap-responsive-layout-in-mobile-convert-to-tabs/31765611

$(window).on('resize', function () {
  var win = $(this); //this = window
  if (win.width() >= 768) {
    $("#home").css("display", "block");
    $("#myrecipes").css("display", "block");
  }
  if (win.width() <= 767) {
    if ($("#hometab>a").is(".active")) {
      $("#home").css("display", "block");
      $("#myrecipes").hide();
    }
  if ($("#ptab>a").is(".active")) {
      $("#home").hide();
      $("#myrecipes").css("display", "block");
    }
  }
});
// #endregion


// #region DOCUMENT.READY START //

$(document).ready(function () {

  // #region hide search results div until populated with data
  $("#searchResult").hide();

  // #endregion


  // #region hide ingredients panel on mobile
  var windowSize = $(window).width();
  if (windowSize <= 767){
    $("#myrecipes").hide();
    if ($("#hometab>a").is(".active")) {
      $("#home").css("display", "block");
      $("#myrecipes").hide();
    }
  }
  // #endregion

  
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
        '<input type="text" class="input form-control" placeholder="Ingredient" name="ingredient">' +
        '<a href="#" class="delete"><i class="fa fa-minus-circle" aria-hidden="true"></i> Remove</a></div>';
      $("#ingredients_input_list").append(ingred);
    }
    else {
      var method = '<div class="added-instruction">' +
        '<textarea class="input form-control" placeholder="Instruction" name="instruction"></textarea>' +
        '<a href="#" class="delete"><i class="fa fa-minus-circle" aria-hidden="true"></i> Remove</a></div>';
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


  // #region AJAX DELETING A RECIPE - CONFIRM WITH USER 

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
        width: 320,
        modal: true,
        buttons: {
          "Delete the recipe": function () {
            $(this).dialog("close");
            var recipe_id = thisrecipeid;
            $.ajax({
              url: '/delete_recipe',
              data: { "recipe_id": recipe_id },
              type: 'POST',
              success: function (response) {
                $("#myrecipesMessages").html(response);
                window.location.href = "/myrecipes?limit=5&offset=0";
              },
              error: function (error) {
                $("#myrecipesMessages").html("There was an error deleting your recipe. Please try again.");
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

  $('#hometab').click(function () {
    $("#home").css("display", "block");
    $("#myrecipes").css("display", "none");
  })
  $('#ptab').click(function () {
    $("#myrecipes").css("display", "block");
    $("#home").css("display", "none");
  })

  // #endregion


  // #region AJAX RATE THIS RECIPE

  $('#rateme').click(function (e) {
    e.preventDefault();
    addVote();
    return false; //return false;  stops page jumping back to top
  });
  function addVote() {
    votes = 1;
    var url = window.location.href;
    recipe_id = url.split("/").pop();
    $.ajax({
      url: '/update_vote/' + recipe_id,
      contentType: 'application/json',
      data: JSON.stringify(votes),
      type: 'POST',
      success: function (response) {
        if (response == 'fail') {
          $("#ratemeMessages").html("You have already voted for this recipe");
        }
        else {
          $("#vote_result").html(response);
        }
      },
      error: function (error) {
        $("#ratemeMessages").html("There was an error rating the recipe. Please try again.");
      }
    });
  }
  // #endregion


  // #region GET CATEGORY FROM SEARCH FILTER AND PASS TO FLASK

  $(function () {
    $("#category-select").change(function (event) {
      event.preventDefault();
      var categorypicked = $('#category-select').find(":selected").text();
      var category = categorypicked.trim();
      $.ajax({
        url: '/filter_by_category/' + category,
        contentType: 'application/json',
        data: JSON.stringify(category),
        type: 'POST',
        success: function (response) {
          $('.initialRecipes').hide();
          $("#searchResult").show();
          $("h3.section-subheading").html("Recipes searched by Category: " + categorypicked);
          $('#cuisine-select').val("Select a Cuisine");
          $('#allergen-select').val("Select an Allergen");
          if (response != "fail") {
            $("#recipeResult").html(response);
          }
          else {
            $("#recipeResult").html("There were no recipes with the Category <span class='search-param'>" + categorypicked + "</span>. <br>Try searching again." );
          }         
          //scroll window to results
          $('html, body').animate({
            scrollTop: $(".results-col").offset().top -300
          }, 'slow');          
        },
        error: function (error) {
          $("#recipeResult").html("There was an error searching recipes. Please try again.");
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
      var cuisine = cuisinepicked.trim();
      $.ajax({
        url: '/filter_by_cuisine/' + cuisine,
        contentType: 'application/json',
        data: JSON.stringify(cuisine),
        type: 'POST',
        success: function (response) {
          $('.initialRecipes').hide();
          $("#searchResult").show();
          $("h3.section-subheading").html("Recipes searched by Cuisine: " + cuisinepicked);
          $('#category-select').val("Select a Category");
          $('#allergen-select').val("Select an Allergen");
          if (response != "fail") {
            $("#recipeResult").html(response);
          }
          else {
            $("#recipeResult").html("There were no recipes found with Cuisine <span class='search-param'>" + cuisinepicked + "</span>. <br>Try searching again." );
          }          
          //scroll window to results
          $('html, body').animate({
            scrollTop: $(".results-col").offset().top -300
          }, 'slow');          
        },
        error: function (error) {
          $("#recipeResult").html("There was an error searching the recipes. Please try again.");
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
      var allergen = allergenpicked.trim();
      $.ajax({
        url: '/filter_by_allergen/' + allergen,
        contentType: 'application/json',
        data: JSON.stringify(allergen),
        type: 'POST',
        success: function (response) {
          $('.initialRecipes').hide();
          $("#searchResult").show();
          $("h3.section-subheading").html("Recipes searched by Allergen: " + allergenpicked);
          $('#category-select').val("Select a Category");
          $('#cuisine-select').val("Select a Cuisine");
          if (response != "fail") {
            $("#recipeResult").html(response);
          }
          else {
            $("#recipeResult").html("There were no recipes found with the Allergen <span class='search-param'>" + allergenpicked + "</span>. <br>Try searching again." );
          }
          //scroll window to results
          $('html, body').animate({
            scrollTop: $(".results-col").offset().top -300
          }, 'slow');
        },
        error: function (error) {
          $("#recipeResult").html("There was an error searching the recipes. Please try again.");
        }
      });
    });
  });

  // #endregion


  // #region GET INGREDIENT FROM SEARCH FILTER AND PASS TO FLASK

  $(function () {
    $('#ingredientFilter').submit(function (event) {
      event.preventDefault();
      var ingredient = $('#searchmain').val();
      $.ajax({
        url: '/filter_by_ingredient',
        data: ingredient,
        type: 'POST',
        success: function (response) {
          $('.initialRecipes').hide();
          $("#searchResult").show();
          $("h3.section-subheading").html("Recipes searched by Ingredient: " + ingredient);
          if (response != "fail") {
            $("#recipeResult").html(response);
          }
          else {
            $("#recipeResult").html("There were no recipes found with <span class='search-param'>" + ingredient + "</span> as the Main Ingredient. <br>Try searching again." );
          }
          //scroll window to results
          $('html, body').animate({
            scrollTop: $(".results-col").offset().top -300
          }, 'slow');
        },
        error: function (error) {
          $("#recipeResult").html("There was an error searching the recipes. Please try again.");
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
      var cuisine = cuisinepicked.trim();
      var category = categorypicked.trim();
      if (category == "Select a Category" || cuisine == "Select a Cuisine") {
        $("#filterMessage").html("You must select a Category and Cuisine");
      }
      else {
        $.ajax({
          url: '/filter_by_catcuis/' + category + '/' + cuisine,
          contentType: 'application/json',
          data: JSON.stringify(cuisine),
          type: 'POST',
          success: function (response) {
            $("#searchResult").show();
            $('.initialRecipes').hide();
            $("h3.section-subheading").html("Recipes searched by Category: " + categorypicked + " and Cuisine: " + cuisinepicked);
            $('#category-select').val("Select a Category");
            $('#allergen-select').val("Select an Allergen");
            if (response != "fail") {
              $("#recipeResult").html(response);
            }
            else {
              $("#recipeResult").html("There were no recipes found with Category <span class='search-param'>" + categorypicked + "</span> and Cuisine <span class='search-param'>" + cuisinepicked + "</span>. <br>Try searching again." );
            }
            //scroll window to results
            $('html, body').animate({
              scrollTop: $(".results-col").offset().top -300
            }, 'slow');
          },
          error: function (error) {
            $("#recipeResult").html("There was an error searching the recipes. Please try again.");
          }
        });
      }
    });
  });


  // #endregion


  // #region SHOW HIDE PAGING BUTTONS ON MYRECIPES 

  var current_path = $(location).attr('pathname');
  if (current_path == "/myrecipes") {
    var url_string = window.location.href;
    var url = new URL(url_string);
    var limit = parseInt(url.searchParams.get("limit"));
    var offset = parseInt(url.searchParams.get("offset"));
    var totalcount = parseInt($("#totalcount").text());
    if (offset == 0) {
      $(".previous").hide();
      $(".next").show();
      $("#numberofpages").html("First page");
    }
    if ((offset + limit) > totalcount) {
      $(".next").hide();
      $("#numberofpages").html("Last page");
    }
  }

 // #endregion


}); // close document.ready


// #endregion

