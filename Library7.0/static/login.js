document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;

    if(username == 'lib' && password == '123@admin') {
        window.location.href = '/main_menu';
    } else {
        fetch('/student_login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                'username': username,
                'password': password
            })
        }).then(function(response) {
            if(response.ok) {
                sessionStorage.setItem('student_id', password);
                window.location.href = '/student_dashboard';
            } else {
                alert('Invalid username or password');
            }
        });
    }
});





