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
