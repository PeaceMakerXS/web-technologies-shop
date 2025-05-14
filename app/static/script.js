document.addEventListener('DOMContentLoaded', function() {
    console.log('Order Form Script loaded');

    // Основные элементы
    const orderForm = document.querySelector('#order-form form');
    console.log(orderForm)

    // Инициализация расчета суммы
    initTotalCalculation();

    // Обработка отправки формы
    if (orderForm) {
        orderForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            try {
                const response = await submitOrderForm(this);
                if (response.ok) {
                    const result = await response.json();
                    showSuccessAlert(result.order_id);
                } else {
                    throw new Error('Ошибка сервера');
                }
            } catch (error) {
                console.error('Order submission error:', error);
                alert('Произошла ошибка: ' + error.message);
            }
        });
    }

    function initTotalCalculation() {
        const productSelect = document.getElementById('product_id');
        const quantityInput = document.getElementById('products_count');

        if (!productSelect || !quantityInput) return;
        function calculateTotal() {
            const selectedOption = productSelect.options[productSelect.selectedIndex];
            const price = parseFloat(selectedOption?.dataset.price) || 0;
            const quantity = parseInt(quantityInput.value) || 1;
            const total = (price * quantity).toFixed(2);

            document.getElementById('total').textContent = total + ' руб.';
        }

        productSelect.addEventListener('change', calculateTotal);
        quantityInput.addEventListener('input', calculateTotal);
        calculateTotal();
    }

    async function submitOrderForm(form) {
        const formData = new FormData(form);

        return await fetch('submit-order', {
            method: 'POST',
            body: formData,
            headers: {
                'Accept': 'application/json'
            }
        });
    }

    function showSuccessAlert(orderId) {
        alert(`Ваш заказ №${orderId} успешно принят!\n\nМы свяжемся с вами в ближайшее время для подтверждения.`);
    }
});