const modalEditPrice = document.getElementById('modalEditPrice');
const editPriceModal = document.getElementById('editPriceModal');
const btnEditPrice = document.getElementById("btnEditPrice");
const btnRefreshNaverPrice = document.getElementById("btnRefreshNaverPrice");
let isLoading = false;


function showLoading() {
  document.getElementById('loadingOverlay').classList.remove('d-none');
}
function hideLoading() {
  document.getElementById('loadingOverlay').classList.add('d-none');
}

// 붙여넣기 필터링
modalEditPrice.addEventListener('paste', function(e) {
  e.preventDefault();
  let pastedData = (e.clipboardData || window.clipboardData).getData('text');
  let filtered = pastedData.replace(/[^0-9]/g, '');
  document.execCommand('insertText', false, filtered);
});

// 입력 중 숫자 아닌 문자 제거
modalEditPrice.addEventListener('input', function(e) {
  let val = e.target.value.replace(/[^0-9]/g, '');
  if (val !== e.target.value) {
    e.target.value = val;
  }
});

editPriceModal.addEventListener('show.bs.modal', function (event) {
    let don = parseInt(document.getElementById('don_price').innerText.replace(/,/g, ''), 10) 
    modalEditPrice.value = don;
    modalEditPrice.placeholder = don;
});
modalEditPrice.addEventListener('click', function() {
  this.select();
});

btnEditPrice.addEventListener("click", () => {
    if (modalEditPrice.value === "") {
        modalEditPrice.focus();
        return;
    }
    customConfirm({
        title: "저장 하시겠습니까?",
        confirmButtonText: "확인",
        cancelButtonText: "취소",
        onConfirm: function() {
            const form = document.getElementById("editPriceForm");
            const data = new FormData(form);

            const elements = form.elements; // 폼 내부의 모든 입력 요소 가져오기
            // 폼 비활성화
            for (let i = 0; i < elements.length; i++) {
                elements[i].disabled = true;
            }
            $.ajax({
                type: "POST",
                url: "/system-manage/gold-price/",
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


btnEditPrice.addEventListener("click", () => {
    if (modalEditPrice.value === "") {
        modalEditPrice.focus();
        return;
    }
    customConfirm({
        title: "저장 하시겠습니까?",
        confirmButtonText: "확인",
        cancelButtonText: "취소",
        onConfirm: function() {
            const form = document.getElementById("editPriceForm");
            const data = new FormData(form);

            const elements = form.elements; // 폼 내부의 모든 입력 요소 가져오기
            // 폼 비활성화
            for (let i = 0; i < elements.length; i++) {
                elements[i].disabled = true;
            }
            $.ajax({
                type: "POST",
                url: "/system-manage/gold-price/",
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

btnRefreshNaverPrice.addEventListener("click", function(e) {
    if (isLoading) {
        e.preventDefault();
        return;
    }
    isLoading = true;
    customConfirm({
        title: "네이버 금 시세를 불러오시겠습니까?",
        confirmButtonText: "확인",
        cancelButtonText: "취소",
        onConfirm: function() {
            showLoading(); // 👈 로딩 띄움
            $.ajax({
                type: "POST",
                url: "/system-manage/gold-price/naver/",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                success: function(data) {
                    hideLoading(); // 👈 로딩 숨김
                    customAlert({ title: 'Success!', text: data.message, icon: 'success', onClose: () => { location.reload(); } });
                },
                error: function(error) {
                    isLoading = false;
                    hideLoading(); // 👈 로딩 숨김
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
