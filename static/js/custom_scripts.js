//AJAX send the signup data to the back end

  $(function () {
    $('#signupForm').submit(function(event) {
      event.preventDefault();
      $.ajax({
        url: '/signup_user',
        data: $('#signupForm').serialize(),
        type: 'POST',
        success: function (response) {
          console.log(response);
          $('#signupModal').modal('show');
          $("#signupMessages").html(response);
        },
        error: function (error) {
          console.log(error);
          $('#signupModal').modal('show');
          $("#signupMessages").html(response);
        }
      });
    });
  });


  //AJAX send the login data to the back end

  $(function () {
    $('#loginForm').submit(function(event) {
      event.preventDefault();
      $.ajax({
        url: '/login_user',
        data: $('#loginForm').serialize(),
        type: 'POST',
        success: function (response) {
          console.log(response);
          $('#loginModal').modal('show');
          $("#loginMessages").html(response);
        },
        error: function (error) {
          console.log(error);
          $('#loginModal').modal('show');
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
