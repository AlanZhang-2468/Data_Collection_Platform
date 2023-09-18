const addInputsBtn = document.getElementById('add-inputs-btn');
const container = document.querySelector('.container');

addInputsBtn.addEventListener('click', function() {
  const newInputContainer = document.createElement('div');
  newInputContainer.classList.add('input-container');

  const newLabel = document.createElement('label');
  newLabel.textContent = '新的选择选项：';

  const newSelect = document.createElement('select');
  newSelect.innerHTML = `
    <option value="option1">选项1</option>
    <option value="option2">选项2</option>
    <option value="option3">选项3</option>
  `;

  const newTextInput = document.createElement('input');
  newTextInput.type = 'text';

  newInputContainer.appendChild(newLabel);
  newInputContainer.appendChild(newSelect);
  newInputContainer.appendChild(document.createElement('br'));
  newInputContainer.appendChild(document.createElement('br'));
  newInputContainer.appendChild(document.createTextNode('新的文本输入：'));
  newInputContainer.appendChild(newTextInput);

  container.insertBefore(newInputContainer, addInputsBtn);
});