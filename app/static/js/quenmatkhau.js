function confirmPasswords() {
    let password = document.getElementById("password").value;
    let retypePassword = document.getElementById("retype_password").value;
    let form = document.getElementById("form-doi-mat-khau");
    if (password !== retypePassword) {
        alert("Mật khẩu và Nhập lại mật khẩu không khớp. Vui lòng kiểm tra lại.");
    }
    else{
        form.submit();
    }
}