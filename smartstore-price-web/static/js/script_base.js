const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
const timeEl = document.getElementById('current-time');

if (timeEl) {
    const weekdays = ['일', '월', '화', '수', '목', '금', '토'];

    function updateTime() {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const weekday = weekdays[now.getDay()];
        const hour = String(now.getHours()).padStart(2, '0');
        const minute = String(now.getMinutes()).padStart(2, '0');

        const formattedTime = `${year}.${month}.${day} (${weekday}) ${hour}:${minute}`;
        timeEl.textContent = formattedTime;
    }

    // 최초 1회 실행
    updateTime();

    // 다음 분이 시작되는 시점까지 대기
    const now = new Date();
    const delayToNextMinute = (60 - now.getSeconds()) * 1000 - now.getMilliseconds();

    setTimeout(() => {
        updateTime(); // 딱 맞춰 갱신
        setInterval(updateTime, 60000); // 이후 60초마다 갱신
    }, delayToNextMinute);
}

// warning | error | success | info | question
function customAlert({ title = '', text = '', icon = 'success', onClose = () => {}}) {
    const preventEnterKeyPropagation = (e) => {
      if (e.key === 'Enter' || e.key === 'Escape') {
        e.preventDefault(); // 기본 동작 방지
        e.stopPropagation();  // `Enter` 키가 뒤에 모달로 전파되지 않도록 막음
        Swal.getConfirmButton().click();  // `Enter`로 Confirm 버튼 클릭
      }
    };

    const preventClickPropagation = (e) => {
      e.stopPropagation();  // SweetAlert2 내부 클릭 이벤트 전파 차단
    };
    Swal.fire({
      title: title,
      text: text,
      icon: icon,
      customClass: {
        confirmButton: 'btn btn-primary waves-effect waves-light'
      },
      buttonsStyling: false,
      didOpen: () => {
        const popup = Swal.getPopup();
        if (popup) {
          // SweetAlert2 모달 클릭 시 이벤트 전파 차단
          popup.addEventListener('mousedown', preventClickPropagation, true);
          // `Enter` 키 이벤트 차단
          document.addEventListener('keydown', preventEnterKeyPropagation, true);
        }
      },
      willClose: () => {
        // 이벤트 리스너 제거
        const popup = Swal.getPopup();
        if (popup) {
          popup.removeEventListener('mousedown', preventClickPropagation, true);
          document.removeEventListener('keydown', preventEnterKeyPropagation, true);
        }
      }
    }).then(() => {
        onClose();
    });
}

function customConfirm({
    title = 'Are you sure?',
    text = '',
    icon = 'question',
    confirmButtonText = '확인',
    cancelButtonText = '취소',
    onConfirm = () => {},
    onCancel = () => {}
  }) {

    const preventEnterKeyPropagation = (e) => {
      if (e.key === 'Enter') {
        e.preventDefault(); // 기본 동작 방지
        e.stopPropagation();
        Swal.getConfirmButton().click(); // Enter → 확인
      } else if (e.key === 'Escape') {
        e.preventDefault(); // 기본 동작 방지
        e.stopPropagation();
        Swal.getCancelButton().click();  // Escape → 취소
      }
    };

    const preventClickPropagation = (e) => {
      e.stopPropagation();  // SweetAlert2 내부 클릭 이벤트 전파 차단
    };


    Swal.fire({
      title: title,
      text: text,
      icon: icon,
      showCancelButton: true,
      confirmButtonText: confirmButtonText,
      cancelButtonText: cancelButtonText,
      customClass: {
        confirmButton: 'btn btn-primary me-1 waves-effect waves-light',
        cancelButton: 'btn btn-outline-secondary waves-effect'
      },
      buttonsStyling: false,
      didOpen: () => {
        const popup = Swal.getPopup();
        if (popup) {
          // SweetAlert2 모달 클릭 시 이벤트 전파 차단
          popup.addEventListener('mousedown', preventClickPropagation, true);
          // `Enter` 키 이벤트 차단
          document.addEventListener('keydown', preventEnterKeyPropagation, true);
        }
      },
      willClose: () => {
        // 이벤트 리스너 제거
        const popup = Swal.getPopup();
        if (popup) {
          popup.removeEventListener('mousedown', preventClickPropagation, true);
          document.removeEventListener('keydown', preventEnterKeyPropagation, true);
        }
      }
    }).then((result) => {
      if (result.isConfirmed) {
        onConfirm();
      } else {
        onCancel();
      }
    });
  }

  function handleLogout(event) {
    event.preventDefault();  // 기본 href 동작을 막습니다.
    customConfirm({
      title: '로그아웃 하시겠습니까?',  
      onConfirm: () => {
            $.ajax({
                type: "POST",
                url: "/system-manage/logout/",  
                headers: {
                    'X-CSRFToken': csrftoken
                },
                datatype: "JSON",
                success: function(data, textStatus, xhr) {
                    const redirectUrl = xhr.getResponseHeader('Location');
                    if (redirectUrl) {
                        window.location.href = redirectUrl;
                    } else {
                        location.reload();
                    }
                },
                error: function(error) {
                  customAlert({ 
                      title: 'Error!', 
                      text: error.status + JSON.stringify(error.responseJSON), 
                      icon: 'error' 
                  });
                },
            });
        },
        onCancel: () => {
            // 취소 시 아무 동작하지 않음
        }
    });
  }