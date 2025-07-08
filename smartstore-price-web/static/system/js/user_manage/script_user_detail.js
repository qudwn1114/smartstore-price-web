const btnEdit = document.getElementById("btnEdit");
const password1 = document.getElementById("new_password1");
const password2 = document.getElementById("new_password2");
const btnPassword = document.getElementById("btnPassword");


//유효성 체크 함수
function validation(){
    return true;
}
btnEdit.addEventListener("click", () => {
    if (!validation()) {
        return;
    }

    customConfirm({
        title: "저장 하시겠습니까?",
        text: "",
        onConfirm: () => {
            const form = document.getElementById("editUserForm");
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
                enctype: "multipart/form-data", //form data 설정
                processData: false, //프로세스 데이터 설정 : false 값을 해야 form data로 인식
                contentType: false, //헤더의 Content-Type을 설정 : false 값을 해야 form data로 인식
                success: function(data) {
                    customAlert({ title: 'Success!', text: data.message, icon: 'success', onClose: () => { location.reload(true); } })
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
                complete: function () {
                    // 요청 완료 후 폼 다시 활성화
                    for (let i = 0; i < elements.length; i++) {
                        elements[i].disabled = false;
                    }
                }
            });
        },
        onCancel: () => {
            // 취소 시 아무 일도 하지 않음
        }
    });
});

function validatePassword() {
    const pw1 = password1.value;
    const pw2 = password2.value;
    const regex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d!@#$%^&*()_\-+={}\[\]:;"'<>,.?/~`|\\]{8,16}$/;
  
    if (regex.test(pw1) && pw1 === pw2) {
      btnPassword.disabled = false;
    } else {
      btnPassword.disabled = true;
    }
  }
  
// 이벤트 연결
password1.addEventListener("input", validatePassword);
password2.addEventListener("input", validatePassword);

btnPassword.addEventListener("click", () => {
    if (document.getElementById("new_password1").value !== document.getElementById("new_password2").value) {
        customAlert({ title: 'Warning!', text: '비밀번호가 일치하지 않습니다.', icon: 'warning' });
        return;
    }

    customConfirm({
        title: "변경 하시겠습니까?",
        text: "",
        onConfirm: () => {
            const form = document.getElementById("formChangePassword");
            const formData = new FormData(form);
            const jsonData = {};

            // FormData를 JSON 형식으로 변환
            formData.forEach((value, key) => {
                jsonData[key] = value;
            });
            jsonData["data_type"] = "PASSWORD";

            const elements = form.elements; // 폼 내부의 모든 입력 요소 가져오기
            // 폼 비활성화
            for (let i = 0; i < elements.length; i++) {
                elements[i].disabled = true;
            }

            $.ajax({
                type: "PUT",
                url: "",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: JSON.stringify(jsonData),
                success: function(data) {
                    customAlert({ title: 'Success!', text: data.message, icon: 'success', onClose: () => { location.reload(true); } })
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
                complete: function () {
                    // 요청 완료 후 폼 다시 활성화
                    for (let i = 0; i < elements.length; i++) {
                        elements[i].disabled = false;
                    }
                }
            });
        },
        onCancel: () => {
            // 취소 시 아무 일도 하지 않음
        }
    });
});