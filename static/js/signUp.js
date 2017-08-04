$(function(){
	$('#btnSignUp').click(function(){
		
		$.ajax({
			url: '/signUp',
			data: $('form').serialize(),
			type: 'POST',
			success: function(response){
				console.log(response);
				alert("Welcome! you can log in now.");
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});
