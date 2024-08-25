function addReview(sanpham_id, khachhang_id) {
    if (khachhang_id == ''){
        pathname = window.location.pathname
        let msg = "Bạn cần phải đăng nhập để sử dụng tính năng này!"
        window.location.href = "/dangnhap?msg="+msg+"&next="+pathname
    }
    else{ //đã đăng nhập rồi
        let binhluan = document.getElementById('binhluan')
        fetch("/api/binhluan", {
        method: "post",
        body: JSON.stringify({
            "sanpham_id": sanpham_id,
            "khachhang_id": khachhang_id,
            "binhluan": binhluan.value
        }),
        headers: {
            'Content-Type': 'application/json'
        }
        }).then(function(res) {
            return res.json();
        }).then(function(data) {
            if (data == false)
                alert("Bạn cần phải mua sản phẩm mới có thể sử dụng tính năng này!");
            else
                window.location.href = window.location.pathname;
        });

    }
}
