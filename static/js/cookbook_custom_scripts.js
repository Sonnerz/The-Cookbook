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
        //Add username to localstorage        
        localStorage.setItem("username", response.username);
        localStorage.setItem("user_id", response._id);
        // Delay before redirect to read message
        var delay = 1500;
        setTimeout(function () { window.location.href = "/profile"; }, delay);
        // window.location.href = "/profile";
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


//   <script>
//     //Add username to localstorage
//     var sc = JSON.stringify({{current_user._id}})
//     localStorage.setItem("username", );
//     var localStorage_current_user_id = localStorage.getItem('username');
//     console.log(localStorage_current_user_id);
// </script>