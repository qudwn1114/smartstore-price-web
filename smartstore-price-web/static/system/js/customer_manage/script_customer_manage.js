const btnSubmit = document.getElementById("btnSubmit");
const phone = document.getElementById('phone');
const membername = document.getElementById('name');

const editCustomerId = document.getElementById('editCustomerId');
const editName = document.getElementById('editName');
const editPhone = document.getElementById('editPhone');
const editBirth = document.getElementById('editBirth');
const editGender = document.getElementById('editGender');
const editComment = document.getElementById('editComment');

const btnEdit = document.getElementById('btnEdit');
const btnDelete = document.getElementById('btnDelete');

phone.addEventListener("input", function (e) {
    this.value = this.value.replace(/[^0-9]/g, ''); // 숫자만 입력
    if (this.value.length > 11) {
      this.value = this.value.slice(0, 11); // 11자리 제한
    }
});

$('#createUser').on('shown.bs.offcanvas', function () {
    // 폼 초기화
    $(this).find('form')[0].reset();
});

$('#editUser').on('hidden.bs.offcanvas', function () {
    // 폼 초기화
    $(this).find('form')[0].reset();
});

//유효성 체크 함수
function validation(){
    if(membername.value == ''){
        membername.focus();
        return false;
    }
    if(phone.value == ''){
        phone.focus();
        return false;
    }
    return true;
}

function editValidation(){
    if(editName.value == ''){
        editName.focus();
        return false;
    }
    if(editPhone.value == ''){
        editPhone.focus();
        return false;
    }
    return true;
}

btnSubmit.addEventListener("click", () => {
    if (!validation()) {
        return;
    }
    customConfirm({
        title: "저장 하시겠습니까?",
        confirmButtonText: "저장",
        cancelButtonText: "취소",
        onConfirm: function() {
            const form = document.getElementById("createUserForm");
            const data = new FormData(form);

            const elements = form.elements; // 폼 내부의 모든 입력 요소 가져오기
            // 폼 비활성화
            for (let i = 0; i < elements.length; i++) {
                elements[i].disabled = true;
            }

            $.ajax({
                type: "POST",
                url: "",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: data,
                enctype: "multipart/form-data", // form data 설정
                processData: false, // 프로세스 데이터 설정 : false 값을 해야 form data로 인식
                contentType: false, // 헤더의 Content-Type을 설정 : false 값을 해야 form data로 인식
                success: function(data) {
                    customAlert({ title: 'Success!', text: data.message, icon: 'success', onClose: () => { location.href = data.url; } });
                },
                error: function(error) {
                    if (error.status == 401) {
                        customAlert({ title: 'Error!', text: '로그인 해주세요.', icon: 'error' });
                    } else if (error.status == 403) {
                        customAlert({ title: 'Error!', text: '권한이 없습니다.', icon: 'error' });
                    } else {
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
        const customerId = this.dataset.customerId;
        const customerName = this.dataset.name;
        customConfirm({
            title: `고객 삭제 하시겠습니까?`,
            text: `${customerName}`,
            confirmButtonText: "확인",
            cancelButtonText: "취소",
            onConfirm: function() {
                $.ajax({
                    type: "POST",
                    url: "/system-manage/customer/delete/",
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    data: {
                        customer_id: customerId
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
});

document.querySelectorAll('.btn-edit-user').forEach(function (el) {
    el.addEventListener('click', function () {
        editCustomerId.value = this.dataset.id;
        editName.value = this.dataset.name;
        editPhone.value = this.dataset.phone;
        editBirth.value = this.dataset.birth;
        editGender.value = this.dataset.gender || '';
        editGender.dispatchEvent(new Event('change'));
        editComment.value = this.dataset.comment || '';
    });
});


btnEdit.addEventListener("click", () => {
    if (!editValidation()) {
        return;
    }
    customConfirm({
        title: "고객 정보 수정 하시겠습니까?",
        confirmButtonText: "저장",
        cancelButtonText: "취소",
        onConfirm: function() {
            const form = document.getElementById("editUserForm");
            const data = new FormData(form);

            const elements = form.elements; // 폼 내부의 모든 입력 요소 가져오기
            // 폼 비활성화
            for (let i = 0; i < elements.length; i++) {
                elements[i].disabled = true;
            }

            $.ajax({
                type: "POST",
                url: "/system-manage/customer/edit/",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: data,
                enctype: "multipart/form-data", // form data 설정
                processData: false, // 프로세스 데이터 설정 : false 값을 해야 form data로 인식
                contentType: false, // 헤더의 Content-Type을 설정 : false 값을 해야 form data로 인식
                success: function(data) {
                    customAlert({ title: 'Success!', text: data.message, icon: 'success', onClose: () => { location.reload(); } });
                },
                error: function(error) {
                    if (error.status == 401) {
                        customAlert({ title: 'Error!', text: '로그인 해주세요.', icon: 'error' });
                    } else if (error.status == 403) {
                        customAlert({ title: 'Error!', text: '권한이 없습니다.', icon: 'error' });
                    } else {
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


btnDelete.addEventListener("click", () => {
    customConfirm({
        title: '삭제 하시겠습니까?',
        confirmButtonText: '확인',
        cancelButtonText: '취소',
        onConfirm: () => {
            btnDelete.disabled = true;
            $.ajax({
                type: "POST",
                url: "/system-manage/customer/delete/",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: {'customer_id': editCustomerId.value},
                datatype: "JSON",
                success: function(data) {
                    customAlert({ 
                        title: 'Success!', 
                        text: data.message, 
                        icon: 'success', 
                        onClose: () => { location.reload(); }
                    });
                },
                error: function(error) {
                    btnDelete.disabled = false;
                    if (error.status == 401) {
                        customAlert({ title: 'Error!', text: '로그인 해주세요.', icon: 'error' });
                    } else if (error.status == 403) {
                        customAlert({ title: 'Error!', text: '권한이 없습니다.', icon: 'error' });
                    } else {
                        customAlert({ 
                            title: 'Error!', 
                            text: error.status + JSON.stringify(error.responseJSON), 
                            icon: 'error' 
                        });
                    }
                },
            });
        },
        onCancel: () => {
            // 취소 시 아무 동작하지 않음
        }
    });
});
