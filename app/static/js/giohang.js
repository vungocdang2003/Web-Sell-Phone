function addToCart(id, name, price, current_user_id, soluongtonkho, soluong, chuyentrang) {
    if (current_user_id == ''){
        pathname = window.location.pathname
        let msg = "Bạn cần phải đăng nhập để sử dụng tính năng này!"
        window.location.href = "/dangnhap?msg="+msg+"&next="+pathname
    }
    else{
        if (soluong == 0){
            let value = document.getElementById("soluong")
            soluong = value.value
        }
        if (soluong > soluongtonkho) {
                alert("Bạn đã nhập quá số lượng tồn kho. Xin vui lòng nhập lại")
        }else{
            fetch("/api/cart", {
                method: "post",
                body: JSON.stringify({
                    "sanpham_id": id,
                    "tensanpham": name,
                    "gia": price,
                    "current_user_id": current_user_id,
                    "soluong": soluong
                }),
                headers: {
                    'Content-Type': 'application/json'
                }
                }).then(function(res) {
                    return res.json();
                }).then(function(data) {
                    let carts = document.getElementsByClassName("cart-counter");
                    for (let d of carts)
                        d.innerText = data.total_quantity;
                    if (chuyentrang == 'True'){
                        window.location.href = "/giohang"
                    }
                });
        }
    }
}

function updateCart(id, obj){
    obj.disabled = true;
    fetch(`/api/cart/${id}`, {
        method: "put",
        body: JSON.stringify({
            "soluong": obj.value
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(function(res) {
        return res.json();
    }).then(function(data) {
        obj.disabled = false;
        console.log(data)
        let carts = document.getElementsByClassName("cart-counter");
        for (let d of carts)
            d.innerText = data.total_quantity;

        let amounts = document.getElementsByClassName("cart-amount");
        for (let d of amounts)
            d.innerText = data.total_amount.toLocaleString("en");
    });
}

function deleteCart(id, obj) {
    if (confirm("Bạn chắc chắn xóa?") === true) {
        obj.disabled = true;
        fetch(`/api/cart/${id}`, {
            method: "delete"
        }).then(function(res) {
            return res.json();
        }).then(function(data) {
            obj.disabled = false;
            let carts = document.getElementsByClassName("cart-counter");
            let t = document.getElementById(`product${id}`);
            if (data.total_quantiy != 0){
                for (let d of carts)
                d.innerText = data.total_quantity;

                let amounts = document.getElementsByClassName("cart-amount");
                for (let d of amounts)
                    d.innerText = data.total_amount.toLocaleString("en");

                t.style.display = "none";
            }else{
                let thongtin = document.getElementById("form-thong-tin");
                thongtin.style.display ="none";
            }

        });
    }
}

function confirmBuy() {
    if (confirm("Bạn chắc chắn mua hàng?") === true) {
        let form = document.getElementById("form-thanh-toan");
        let phone = document.getElementById("phone");
        let address = document.getElementById("address");
        if (!phone && !address){
            form.submit();
        }
        if (phone.checkValidity() && address.checkValidity()){
            form.submit();
        }
        else{
            alert("Dữ liệu không hợp lệ. Vui lòng kiểm tra lại.");
        }
    }
}
