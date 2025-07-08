const search_keyword = document.getElementById('search_keyword');
const price = document.getElementById('price');
const editPriceModal = document.getElementById('editPriceModal');
const btnEditPrice = document.getElementById("btnEditPrice");
const btnRefreshNaverPrice = document.getElementById("btnRefreshNaverPrice");
const btnBulkUpdate = document.getElementById("btnBulkUpdate");
const btnBulkApply = document.getElementById("btnBulkApply");

let isLoading = false;

function showLoading() {
  document.getElementById('loadingOverlay').classList.remove('d-none');
}
function hideLoading() {
  document.getElementById('loadingOverlay').classList.add('d-none');
}

function setupNumberOnlyInput(input) {
  // 붙여넣기 필터링
  input.addEventListener('paste', function(e) {
    e.preventDefault();
    let pastedData = (e.clipboardData || window.clipboardData).getData('text');
    let filtered = pastedData.replace(/[^0-9]/g, '');
    document.execCommand('insertText', false, filtered);
  });

  // 입력 중 숫자 아닌 문자 제거
  input.addEventListener('input', function(e) {
    let val = e.target.value.replace(/[^0-9]/g, '');
    if (val !== e.target.value) {
      e.target.value = val;
    }
  });
}

document.querySelectorAll('.number-only').forEach(input => {
  setupNumberOnlyInput(input);
});

function setupNumberAndDecimalInput(input) {
  input.addEventListener('paste', function(e) {
    e.preventDefault();
    let pastedData = (e.clipboardData || window.clipboardData).getData('text');

    // 숫자, 점, 마이너스만 남기기
    let filtered = pastedData.replace(/[^0-9\.\-]/g, '');

    // 마이너스가 맨 앞에만 오도록 조정
    const minusIndex = filtered.indexOf('-');
    filtered = filtered.replace(/-/g, '');
    if (minusIndex === 0) {
      filtered = '-' + filtered;
    }

    // 점이 여러 개면 첫 번째만 남기고 제거
    const firstDotIndex = filtered.indexOf('.');
    if (firstDotIndex !== -1) {
      filtered = filtered.slice(0, firstDotIndex + 1) + filtered.slice(firstDotIndex + 1).replace(/\./g, '');
    }

    document.execCommand('insertText', false, filtered);
  });

  // 입력 중 실시간 필터링
  input.addEventListener('input', function(e) {
    let val = e.target.value;

    // 숫자, 점, 마이너스만 남기기
    val = val.replace(/[^0-9\.\-]/g, '');

    // 마이너스가 맨 앞에만 오도록 조정
    const minusIndex = val.indexOf('-');
    val = val.replace(/-/g, '');
    if (minusIndex === 0) {
      val = '-' + val;
    }

    // 점이 여러 개면 첫 번째만 남기고 제거
    const firstDotIndex = val.indexOf('.');
    if (firstDotIndex !== -1) {
      val = val.slice(0, firstDotIndex + 1) + val.slice(firstDotIndex + 1).replace(/\./g, '');
    }

    if (val !== e.target.value) {
      e.target.value = val;
    }
  });
}

// 적용 예시
document.querySelectorAll('.number-decimal-only').forEach(input => {
  setupNumberAndDecimalInput(input);
});



editPriceModal.addEventListener('show.bs.modal', function (event) {
    let don = parseInt(document.getElementById('don_price').innerText.replace(/,/g, ''), 10) 
    price.value = don;
    price.placeholder = don;
});
price.addEventListener('click', function() {
  this.select();
});

search_keyword.addEventListener('click', function() {
  this.select();
});

btnEditPrice.addEventListener("click", () => {
    if (price.value === "") {
        price.focus();
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



btnBulkUpdate.addEventListener("click", function(e) {
    const don = btnBulkUpdate.getAttribute("data-don-price");
    customConfirm({
        title: "시세를 일괄 적용 하시겠습니까?",
        text: `1돈 : ${numberWithCommas(don)}원`,
        confirmButtonText: "확인",
        cancelButtonText: "취소",
        onConfirm: function() {
            $.ajax({
                type: "POST",
                url: "/system-manage/product/bulk-update/",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: {don: don},
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
