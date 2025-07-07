const optionModal = document.getElementById("optionModal");
const modalFetchOption = document.getElementById("modalFetchOption");
const modalOptionDescription = document.getElementById("modalOptionDescription");
const modalOptionContent = document.getElementById("modalOptionContent");

optionModal.addEventListener('show.bs.modal', function (event) {
    // 모달이 열릴 때 입력 필드를 초기화합니다.
    const button = event.relatedTarget;
    const product_id = button.getAttribute("data-product-id");
    const product_name = button.getAttribute("data-name");
    modalOptionDescription.textContent = `상품명: ${product_name}`;
    modalFetchOption.setAttribute("data-product-id", product_id);

    loadOptionContent(product_id);
});

modalFetchOption.addEventListener("click", function () {
  const productId = this.getAttribute("data-product-id");
  customConfirm({
            title: "옵션을 동기화 하시겠습니까?",
            text: "동기화 시 기존 옵션 데이터는 사라집니다.",
            confirmButtonText: "확인",
            cancelButtonText: "취소",
            onConfirm: function() {
                modalFetchOption.disabled = true; // 버튼 비활성화
                $.ajax({
                    type: "POST",
                    url: `/system-manage/product/${productId}/option/fetch/`,
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    data: JSON.stringify({}),
                    dataType: "json",
                    success: function(data) {
                        customAlert({ title: 'Success!', text: data.message, icon: 'success', onClose: () => { loadOptionContent(productId); } });
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
                        modalFetchOption.disabled = false; // 버튼 활성화
                    }
                });
            },
            onCancel: function() {
                // 취소 시 아무 동작도 하지 않음
            }
    });
});

function loadOptionContent(product_id) {
    $.ajax({
        url: `/system-manage/product/${product_id}/option/`,
        type: "GET",
        success: function(data) {
            console.log("옵션 불러오기 성공:", data);
            drawOptionContent(data);
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
    });
}

function drawOptionContent(data) {
    const productId = data.product_id;
    const optionGroups = data.option_group_names;
    const options = data.options;
    const optionGroupFlag = data.option_group_flag;

    if (optionGroups.length === 0) {
        modalOptionContent.innerHTML = "<p>이 상품에는 옵션 그룹이 없습니다.</p>";
        return;
    }
    // 테이블 헤더 생성
    let theadHTML = '<thead><tr>';
    optionGroups.forEach(group => {
    theadHTML += `<th>${group}</th>`;
    });
    theadHTML += `
    <th>중량</th>
    <th>부가비</th>
    <th>배율</th>
    <th>옵션가격</th>
    </tr></thead>`;

    // 테이블 바디 생성
    let tbodyHTML = '<tbody class="table-border-bottom-0">';
    options.forEach(option => {
    tbodyHTML += `<tr data-option-id="${option.id}">`;

    // 옵션 그룹 이름들 (최대 3개)
    const nameFields = ['option_name1', 'option_name2', 'option_name3'];
    for (let i = 0; i < optionGroups.length; i++) {
      tbodyHTML += `<td>${option[nameFields[i]] || ''}</td>`;
    }

    tbodyHTML += `
      <td><input type="text" class="form-control form-control-sm gold-input" placeholder="${stripDecimal(option.gold)}" value="${stripDecimal(option.gold)}"></td>
      <td><input type="text" class="form-control form-control-sm sub-cost-input" placeholder="${option.sub_cost}" value="${option.sub_cost}"></td>
      <td><input type="text" class="form-control form-control-sm markup-rate-input" placeholder="${stripDecimal(option.markup_rate)}" value="${stripDecimal(option.markup_rate)}"></td>
      <td>${numberWithCommas(option.price)}원</td>
    `;
    tbodyHTML += '</tr>';
  });
  tbodyHTML += '</tbody>';
  // 저장 버튼 추가
    const saveSectionHTML = `
    <div class="form-check my-3">
        <input class="form-check-input" type="checkbox" value="" id="optionGroupFlagCheckbox" ${optionGroupFlag ? 'checked' : ''}>
        <label class="form-check-label" for="optionGroupFlagCheckbox">
        판매가 일괄 변경 시 포함 여부
        </label>
    </div>

    <div class="d-grid">
        <button type="button" class="btn btn-primary" id="save-option-button">
        저장
        </button>
    </div>
    `;

    // 전체 테이블 구성
const tableHTML = `
    <div class="table-responsive text-nowrap">
      <table class="table table-sm table-hover">
        ${theadHTML}
        ${tbodyHTML}
      </table>
      ${saveSectionHTML}
    </div>
  `;

    // 렌더링
    modalOptionContent.innerHTML = tableHTML;
    const subCostInputs = modalOptionContent.querySelectorAll('.sub-cost-input');
        subCostInputs.forEach(input => {
        setupNumberOnlyInput(input);
        enableSelectAllOnClick(input);
    });
    const goldInputs = modalOptionContent.querySelectorAll('.gold-input');
    goldInputs.forEach(input => {
        setupNumberAndDecimalInput(input);
        enableSelectAllOnClick(input);
    });
    const markupRateInputs = modalOptionContent.querySelectorAll('.markup-rate-input');
    markupRateInputs.forEach(input => {
        setupNumberAndDecimalInput(input);
        enableSelectAllOnClick(input);
    });

    const saveBtn = modalOptionContent.querySelector('#save-option-button');
    saveBtn.addEventListener('click', function() {
        const rows = modalOptionContent.querySelectorAll('tbody tr');
        const optionDataList = [];

        for (let i = 0; i < rows.length; i++) {
            const row = rows[i];
            const optionId = row.getAttribute('data-option-id');
            const goldInput = row.querySelector('.gold-input');
            const subCostInput = row.querySelector('.sub-cost-input');
            const markupRateInput = row.querySelector('.markup-rate-input');

            const gold = goldInput.value.trim();
            const subCost = subCostInput.value.trim();
            const markupRate = markupRateInput.value.trim();

            const rowNum = i + 1;

            if (gold === '' || isNaN(gold)) {
                customAlert({
                title: 'Error!',
                text: `중량 값을 올바르게 입력해주세요. (행 ${rowNum})`,
                icon: 'error'
                });
                goldInput.focus();
                return;
            }

            if (subCost === '' || isNaN(subCost) || !Number.isInteger(Number(subCost))) {
                customAlert({
                title: 'Error!',
                text: `부가비 값을 올바른 정수로 입력해주세요. (행 ${rowNum})`,
                icon: 'error'
                });
                subCostInput.focus();
                return;
            }

            if (markupRate === '' || isNaN(markupRate)) {
                customAlert({
                title: 'Error!',
                text: `배율 값을 올바르게 입력해주세요. (행 ${rowNum})`,
                icon: 'error'
                });
                markupRateInput.focus();
                return;
            }

            optionDataList.push({
                id: optionId,
                gold: parseFloat(gold),
                sub_cost: parseInt(subCost),
                markup_rate: parseFloat(markupRate)
            });
            }
        // 체크박스 상태
        const flag = document.getElementById('optionGroupFlagCheckbox')?.checked;
        customConfirm({
            title: "수정 하시겠습니까?",
            confirmButtonText: "확인",
            cancelButtonText: "취소",
            onConfirm: function() {
                saveBtn.disabled = true; // 버튼 비활성화
                $.ajax({
                    type: "POST",
                    url: `/system-manage/product/${productId}/option/edit/`,
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    data: JSON.stringify({options: optionDataList, option_group_flag: flag}),
                    dataType: "json",
                    success: function(data) {
                        customAlert({ title: 'Success!', text: data.message, icon: 'success', onClose: () => { loadOptionContent(productId); } });
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
                        saveBtn.disabled = false; // 버튼 활성화
                    }
                });
            },
            onCancel: function() {
                // 취소 시 아무 동작도 하지 않음
            }
        });


    });

}

function enableSelectAllOnClick(input) {
  input.addEventListener('click', function () {
    input.select();
  });
}
    
function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function stripDecimal(value, maxPlaces = 5) {
  if (isNaN(value) || value === null || value === '') return value;

  let num = parseFloat(value);
  if (isNaN(num)) return value;

  // 소수점 maxPlaces 자리까지 자르고, 뒤에 불필요한 0 제거
  let fixed = num.toFixed(maxPlaces);
  return fixed.replace(/\.?0+$/, '');  // 소수점 뒤 0 제거
}