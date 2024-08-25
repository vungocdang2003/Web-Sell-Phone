function add_to_gio_sanpham(id, name, price){
    let url = new URL(window.location.href);
    fetch("/api/giosanpham", {
        method: "post",
        body: JSON.stringify({
            "id": id,
            "name": name,
            "price": price
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(function(res) {
        return res.json();
    }).then(function(data) {
        window.location.href = url;
    });
}

function update_gio_sanpham(id, obj) {
    obj.disabled = true;
    fetch(`/api/giosanpham/${id}`, {
        method: "put",
        body: JSON.stringify({
            "quantity": obj.value
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(function(res) {
        return res.json();
    }).then(function(data) {
        obj.disabled = false;
        let carts = document.getElementsByClassName("cart-counter");
        for (let d of carts)
            d.innerText = data.total_quantity;
        let amounts = document.getElementsByClassName("cart-amount");
        for (let d of amounts)
            d.innerText = data.total_amount.toLocaleString("en");
        let tien = document.getElementById("tien");
        let tiendu = document.getElementById("tiendu");
        tien.value = ""
        tiendu.value = ""
    });
}

function delete_gio_sanpham(id, obj) {
    if (confirm("Bạn chắc chắn xóa?") === true) {
        obj.disabled = true;
        fetch(`/api/giosanpham/${id}`, {
            method: "delete"
        }).then(function(res) {
            return res.json();
        }).then(function(data) {
            obj.disabled = false;
            let carts = document.getElementsByClassName("cart-counter");
            for (let d of carts)
                d.innerText = data.total_quantity;

            let amounts = document.getElementsByClassName("cart-amount");
            for (let d of amounts)
                d.innerText = data.total_amount.toLocaleString("en");


            let t = document.getElementById(`product${id}`);
            t.style.display = "none";
            let tien = document.getElementById("tien");
            let tiendu = document.getElementById("tiendu");
            tien.value = "";
            tiendu.value = "";
        });
    }
}

function tinh_tien_du(){
    let tien = document.getElementById("tien");
    let tiendu = document.getElementById("tiendu");
    let tongtien = document.getElementById("tong_tien").innerText;
    tongtien = tongtien.replace(/,/g, ''); // thay thế toàn bộ (gloabal) có dấu ‘,’ trong ô Tổng tiền
    tongtien = parseFloat(tongtien);
    tien = parseFloat(tien.value);
    if (tien < tongtien){
        alert('Số tiền bạn nhập không hợp lệ!');
    }else{
        tiendu.value = tien - tongtien;
    }
}

function lap_hoa_don(){
    if(confirm("Bạn chắc chắn mua hàng?") === true){
        let form = document.getElementById("form-thanh-toan");
        let tien = document.getElementById("tien");
        let tiendu = document.getElementById("tiendu");
        let tongtien = document.getElementById("tong_tien").innerText;
        tongtien = tongtien.replace(/,/g, ''); // Loại bỏ tất cả các dấu phẩy từ chuỗi
        tongtien = parseFloat(tongtien);
        tien = parseFloat(tien.value);
        if (tiendu.value >= 0 && (tien - tongtien) >= 0){
            form.submit();
        }else{
            alert("Đơn hàng không hợp lệ!")
        }
    }

}
