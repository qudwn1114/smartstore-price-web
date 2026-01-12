const order_status = $('#order_status');

const editOrderId = document.getElementById('editOrderId');
const editOrderName = document.getElementById('editOrderName');
const editOrderDate = document.getElementById('editOrderDate');
const editOrderStatus = $('#editOrderStatus');
const editTotalPrice = document.getElementById('editTotalPrice');
const editComment = document.getElementById('editComment');

const btnEdit = document.getElementById('btnEdit');
const btnDelete = document.getElementById('btnDelete');

$('#customers').selectpicker({
  container: '#createOrder .offcanvas-body'
});

$('#editCustomers').selectpicker({
  container: '#editOrder .offcanvas-body'
});

function renderBadges(option) {
    if (!option.id) {
        return option.text;
    }
    var $badge =
        "<span class='badge badge-dot bg-" + $(option.element).data('label') + " me-2'> " + '</span>' + option.text;

    return $badge;
}

$('.select2-order-status').each(function () {
    const $select = $(this);

    // 🔥 중복 초기화 방지
    if ($select.hasClass('select2-hidden-accessible')) {
        return;
    }
    select2Focus($select);
    $select.select2({
        placeholder: 'Select value',
        dropdownParent: $('body'),   // 🔥 테이블 필수
        templateResult: renderBadges,
        templateSelection: renderBadges,
        minimumResultsForSearch: -1,
        width: '100%',
        escapeMarkup: function (es) {
            return es;
        }
    });
});

if (editOrderStatus.length) {
    select2Focus(editOrderStatus);
    editOrderStatus.wrap('<div class="position-relative"></div>').select2({
    placeholder: 'Select value',
    dropdownParent: editOrderStatus.parent(),
    templateResult: renderBadges,
    templateSelection: renderBadges,
    minimumResultsForSearch: -1,
    escapeMarkup: function (es) {
        return es;
    }
    });
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
$('#editOrder').on('hidden.bs.offcanvas', function () {
    // 폼 초기화
    $(this).find('form')[0].reset();
});

function editValidation(){
    if(editOrderName.value == ''){
        editOrderName.focus();
        return false;
    }
    if(editOrderDate.value == ''){
        editOrderDate.focus();
        return false;
    }
    if(editTotalPrice.value == ''){
        editTotalPrice.focus();
        return false;
    }
    return true;
}


document.querySelectorAll('.btn-delete').forEach(function (btn) {
    btn.addEventListener('click', function () {
        const orderId = this.dataset.orderId;
        const orderName = this.dataset.order_name;
        customConfirm({
            title: `주문 삭제 하시겠습니까?`,
            text: `${orderName}`,
            confirmButtonText: "확인",
            cancelButtonText: "취소",
            onConfirm: function() {
                $.ajax({
                    type: "POST",
                    url: "/system-manage/order/delete/",
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    data: {
                        order_id: orderId
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

document.querySelectorAll('.btn-edit-order').forEach(function (el) {
    el.addEventListener('click', function () {
        editOrderId.value = this.dataset.id;
        editOrderName.value = this.dataset.order_name;
        editOrderDate.value = this.dataset.order_date;
        editTotalPrice.value = this.dataset.total_price;
        editComment.value = this.dataset.comment || '';
        editOrderStatus.val(this.dataset.status).trigger('change');
        $('#editCustomers').selectpicker('val', this.dataset.customer_id || '');
    });
});


btnEdit.addEventListener("click", () => {
    if (!editValidation()) {
        return;
    }
    customConfirm({
        title: "주문 정보 수정 하시겠습니까?",
        confirmButtonText: "저장",
        cancelButtonText: "취소",
        onConfirm: function() {
            const form = document.getElementById("editOrderForm");
            const data = new FormData(form);

            const elements = form.elements; // 폼 내부의 모든 입력 요소 가져오기
            // 폼 비활성화
            for (let i = 0; i < elements.length; i++) {
                elements[i].disabled = true;
            }

            $.ajax({
                type: "POST",
                url: "/system-manage/order/edit/",
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
                url: "/system-manage/order/delete/",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: {'order_id': editOrderId.value},
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


$(document).on('select2:select', '.select2-order-status', function (e) {
    const $select = $(this);
    const orderId = $select.data('order-id');
    const newStatus = $select.val();
    const prevStatus = $select.data('prev-status');

    // 값이 같으면 무시
    if (newStatus === String(prevStatus)) return;

    updateOrderStatus(orderId, newStatus, $select, prevStatus);
});

function updateOrderStatus(orderId, status, $select, prevStatus) {
    $.ajax({
        url: '/system-manage/order/status/',   // 너 URL로 변경
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: {
            order_id: orderId,
            status: status,
        },
        success: function (res) {
            $select.data('prev-status', status);
        },
        error: function () {
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
            rollbackSelect($select, prevStatus);
        }
    });
}
