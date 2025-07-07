const btnCreateProduct = document.getElementById("btnCreateProduct");
const modalCreateChannelProductNo = document.getElementById("modalCreateChannelProductNo");
const modalCreateGold = document.getElementById("modalCreateGold");
const modalCreateLaborCost = document.getElementById("modalCreateLaborCost");
const modalCreateSubCost = document.getElementById("modalCreateSubCost");
const modalCreateMarkupRate = document.getElementById("modalCreateMarkupRate");
const createProductModal = document.getElementById("createProductModal");

const modalEditProductDescription = document.getElementById("modalEditProductDescription");
const modalEditProductId = document.getElementById("modalEditProductId");
const modalEditChannelProductNo = document.getElementById("modalEditChannelProductNo");
const modalEditGold = document.getElementById("modalEditGold");
const modalEditLaborCost = document.getElementById("modalEditLaborCost");
const modalEditSubCost = document.getElementById("modalEditSubCost");
const modalEditMarkupRate = document.getElementById("modalEditMarkupRate");
const editProductModal = document.getElementById("editProductModal");


createProductModal.addEventListener('show.bs.modal', function (event) {
    // 모달이 열릴 때 입력 필드를 초기화합니다.
    modalCreateChannelProductNo.value = "";
    modalCreateGold.value = "";
    modalCreateLaborCost.value = "";
    modalCreateSubCost.value = "";
    modalCreateMarkupRate.value = ""
});


editProductModal.addEventListener('show.bs.modal', function (event) {
    // 모달이 열릴 때 입력 필드를 초기화합니다.
    const button = event.relatedTarget;
    modalEditProductId.value = button.getAttribute("data-product-id");
    modalEditProductDescription.textContent = `상품명: ${button.getAttribute("data-name")}`;
    modalEditChannelProductNo.value = button.getAttribute("data-channel-product-no");
    modalEditGold.value = button.getAttribute("data-gold");
    modalEditGold.placeholder = button.getAttribute("data-gold");
    modalEditLaborCost.value = button.getAttribute("data-labor-cost");
    modalEditLaborCost.placeholder = button.getAttribute("data-labor-cost");
    modalEditSubCost.value = button.getAttribute("data-sub-cost");
    modalEditSubCost.placeholder = button.getAttribute("data-sub-cost");
    modalEditMarkupRate.value = button.getAttribute("data-markup-rate");
    modalEditMarkupRate.placeholder = button.getAttribute("data-markup-rate");
});

modalEditGold.addEventListener('click', function() {
  this.select();
});

modalEditLaborCost.addEventListener('click', function() {
  this.select();
});

modalEditSubCost.addEventListener('click', function() {
  this.select();
});

modalEditMarkupRate.addEventListener('click', function() {
  this.select();
});

btnCreateProduct.addEventListener("click", () => {
    if (modalCreateChannelProductNo.value === "") {
        modalCreateChannelProductNo.focus();
        return;
    }
    if (modalCreateGold.value === "") {
        modalCreateGold.focus();
        return;
    }
    if (modalCreateLaborCost.value === "") {
        modalCreateLaborCost.focus();
        return;
    }
    if (modalCreateSubCost.value === "") {
        modalCreateSubCost.focus();
        return;
    }
    if (modalCreateMarkupRate.value === "") {
        modalCreateMarkupRate.focus();
        return;
    }
    customConfirm({
        title: "등록 하시겠습니까?",
        confirmButtonText: "확인",
        cancelButtonText: "취소",
        onConfirm: function() {
            const form = document.getElementById("createProductForm");
            const data = new FormData(form);

            const elements = form.elements; // 폼 내부의 모든 입력 요소 가져오기
            // 폼 비활성화
            for (let i = 0; i < elements.length; i++) {
                elements[i].disabled = true;
            }
            $.ajax({
                type: "POST",
                url: "/system-manage/product/create/",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: data,
                enctype: "multipart/form-data", //form data 설정
                processData: false, //프로세스 데이터 설정 : false 값을 해야 form data로 인식
                contentType: false, //헤더의 Content-Type을 설정 : false 값을 해야 form data로 인식
                success: function(data) {
                    customAlert({ title: 'Success!', text: data.message, icon: 'success', onClose: () => { location.reload(); } });
                },
                error: function(error) {
                    if (error.status == 401) {
                        customAlert({ title: 'Error!', text: '로그인 해주세요.', icon: 'error' });
                    }
                    else if (error.status == 403) {
                        customAlert({ title: 'Error!', text: '권한이 없습니다.', icon: 'error' });
                    }
                    else {
                        customAlert({ title: 'Error!', text: error.status + JSON.stringify(error.responseJSON), icon: 'error' });
                    }
                },
                complete: function() {
                    // 요청 완료 후 폼 다시 활성화
                    for (let i = 0; i < elements.length; i++) {
                        elements[i].disabled = false;
                    }
                }
            });
        },
        onCancel: function() {
            // 취소 시 아무 동작도 하지 않음
        }
    });
});


btnEditProduct.addEventListener("click", () => {
    if (modalEditProductId.value === "") {
        customAlert({ title: 'Error!', text: '상품 ID ERROR', icon: 'error' });
        return;
    }
    if (modalEditGold.value === "") {
        modalEditGold.focus();
        return;
    }
    if (modalEditLaborCost.value === "") {
        modalEditLaborCost.focus();
        return;
    }
    if (modalEditSubCost.value === "") {
        modalEditSubCost.focus();
        return;
    }
    if (modalEditMarkupRate.value === "") {
        modalEditMarkupRate.focus();
        return;
    }
    customConfirm({
        title: "수정 하시겠습니까?",
        confirmButtonText: "확인",
        cancelButtonText: "취소",
        onConfirm: function() {
            const form = document.getElementById("editProductForm");
            const data = new FormData(form);

            const elements = form.elements; // 폼 내부의 모든 입력 요소 가져오기
            // 폼 비활성화
            for (let i = 0; i < elements.length; i++) {
                elements[i].disabled = true;
            }
            $.ajax({
                type: "POST",
                url: "/system-manage/product/edit/",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: data,
                enctype: "multipart/form-data", //form data 설정
                processData: false, //프로세스 데이터 설정 : false 값을 해야 form data로 인식
                contentType: false, //헤더의 Content-Type을 설정 : false 값을 해야 form data로 인식
                success: function(data) {
                    customAlert({ title: 'Success!', text: data.message, icon: 'success', onClose: () => { location.reload(); } });
                },
                error: function(error) {
                    if (error.status == 401) {
                        customAlert({ title: 'Error!', text: '로그인 해주세요.', icon: 'error' });
                    }
                    else if (error.status == 403) {
                        customAlert({ title: 'Error!', text: '권한이 없습니다.', icon: 'error' });
                    }
                    else {
                        customAlert({ title: 'Error!', text: error.status + JSON.stringify(error.responseJSON), icon: 'error' });
                    }
                },
                complete: function() {
                    // 요청 완료 후 폼 다시 활성화
                    for (let i = 0; i < elements.length; i++) {
                        elements[i].disabled = false;
                    }
                }
            });
        },
        onCancel: function() {
            // 취소 시 아무 동작도 하지 않음
        }
    });
});

document.querySelectorAll('.btn-delete').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const productId = this.dataset.productId;
            const productName = this.dataset.name;
            customConfirm({
                title: `${productName}\n상품을 삭제 하시겠습니까?`,
                confirmButtonText: "확인",
                cancelButtonText: "취소",
                onConfirm: function() {
                    $.ajax({
                        type: "POST",
                        url: "/system-manage/product/delete/",
                        headers: {
                            'X-CSRFToken': csrftoken
                        },
                        data: {
                            product_id: productId
                        },
                        success: function(data) {
                            customAlert({ title: 'Success!', text: data.message, icon: 'success', onClose: () => { location.reload(); } });
                        },
                        error: function(error) {
                            if (error.status == 401) {
                                customAlert({ title: 'Error!', text: '로그인 해주세요.', icon: 'error' });
                            }
                            else if (error.status == 403) {
                                customAlert({ title: 'Error!', text: '권한이 없습니다.', icon: 'error' });
                            }
                            else {
                                customAlert({ title: 'Error!', text: error.status + JSON.stringify(error.responseJSON), icon: 'error' });
                            }
                        }
                    });
                },
                onCancel: function() {
                    // 취소 시 아무 동작도 하지 않음
                }
            });
        });
    }
);