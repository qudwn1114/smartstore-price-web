const btn_delete = document.getElementById("btn-delete");

btn_delete.addEventListener("click", () => {
    customConfirm({
        title: '삭제 하시겠습니까?',
        confirmButtonText: '확인',
        cancelButtonText: '취소',
        onConfirm: () => {
            btn_delete.disabled = true;
            $.ajax({
                type: "DELETE",
                url: "",  // 서버 API 엔드포인트 추가
                headers: {
                    'X-CSRFToken': csrftoken
                },
                datatype: "JSON",
                success: function(data) {
                    customAlert({ 
                        title: 'Success!', 
                        text: data.message, 
                        icon: 'success', 
                        onClose: () => { location.href = data.url; }
                    });
                },
                error: function(error) {
                    btn_delete.disabled = false;
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
