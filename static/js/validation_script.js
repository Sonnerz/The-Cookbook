$(document).ready(function(){


		$('#signupForm').validate({
	    rules: {	  
			signupUsername: {
				minlength: 1,
				maxlength: 50,
	      required: true
	    },
		  
			signupPassword: {
				required: true,
				minlength: 1,
				maxlength: 8
			},
			confirmPassword: {
				required: true,
				minlength: 1,
				maxlength: 8,
				// equalTo: "#signupPassword"
			},
		  
		  agree: "required"
		  
	    },
			highlight: function(element) {
				$(element).closest('.control-group').removeClass('valid').addClass('error');
			},
			success: function(element) {
				element
				.text('OK!').addClass('valid')
				.closest('.control-group').removeClass('error').addClass('valid');
			}
	  });

}); // end document.ready