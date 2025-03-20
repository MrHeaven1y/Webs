
document.addEventListener('DOMContentLoaded', () => {

    const billingToggle = document.getElementById('billing-toggle');
    const priceElements = document.querySelectorAll('.price');
    const toggleLabels = document.querySelectorAll('.toggle-label');
    
    const monthlyPrices = ['$19', '$49', '$99'];
    const annualPrices = ['$15', '$39', '$79'];
    
    billingToggle.addEventListener('change', function() {
        toggleLabels[0].classList.toggle('active');
        toggleLabels[1].classList.toggle('active');
        
        priceElements.forEach((element, index) => {
            if (this.checked) {
                element.innerHTML = annualPrices[index] + '<span class="price-period">/mo</span>';
            } else {
                element.innerHTML = monthlyPrices[index] + '<span class="price-period">/mo</span>';
            }
        });
    });
})