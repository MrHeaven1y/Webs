document.addEventListener('DOMContentLoaded', () => {
    const dot = document.getElementById('dot');
    const circle = document.getElementById("circle");
    const radiusInput = document.getElementById('radius');
    const radiusValue = document.getElementById("radiusValue");
    const angleInput = document.getElementById("angleInput");
    const angleValue = document.getElementById("angleValue");
    const pos = document.getElementById("pos");
    const opacityInput = document.getElementById("opacity");
    const opacityValue = document.getElementById("opacityValue");
    const dotOpacity = document.getElementById('dotOpacity');
    const dotOpacityValue = document.getElementById('dotOpacityValue');
    const rotation = document.getElementById('rot');
    const counterRotation = document.getElementById('counter-clockwise');
    const tempThetaValue = document.getElementById('tempThetaValue');
    const thetaValue = document.getElementById('thetaValue');
    const eulerValue = document.getElementById('eulerValue');
    
    let currentRotation = 0;
    let animationId = null;
    let rotationTarget = 0;
    let rotationSpeed = 0;
    let isAnimating = false;
    
    // Initialize values
    angleValue.textContent = angleInput.value;
    radiusValue.textContent = (radiusInput.value / 10).toFixed(1);
    opacityValue.textContent = opacityInput.value;

    const updateDotPosition = (angle, radius) => {
        const radian = angle * (Math.PI / 180);
        const x = Math.cos(radian);
        const y = Math.sin(radian);

        if (angle % 180 === 0 || angle === 0) {
            pos.textContent = `Position: ${(radius / 10 * x).toFixed(2)} + ${(radius / 10 * 0).toFixed(2)}i`;
        } else if (angle === 90 || angle === 270) {
            pos.textContent = `Position: ${(radius / 10 * 0).toFixed(2)} + ${(radius / 10 * y).toFixed(2)}i`;
        } else {
            pos.textContent = `Position: ${(radius / 10 * x).toFixed(2)} + ${(radius / 10 * y).toFixed(2)}i`;
        }
        circle.style.transform = `rotate(${-radian}rad)`;
    };

    const updateCircle = () => {
        const radius = radiusInput.value;
        const opacity = opacityInput.value;

        radiusValue.textContent = (radius / 10).toFixed(1);
        opacityValue.textContent = opacity;
        circle.style.width = `${2 * radius}px`;
        circle.style.height = `${2 * radius}px`;
        circle.style.borderColor = `rgba(52, 152, 219, ${opacity})`;
    };

    angleInput.addEventListener('input', () => {
        const angle = angleInput.value;
        angleValue.textContent = angle;
        updateDotPosition(angle, radiusInput.value);
        updatePositionEuler();
    });

    radiusInput.addEventListener('input', () => {
        updateCircle();
        const angle = angleInput.value;
        updateDotPosition(angle, radiusInput.value);
        updatePositionEuler();
    });

    dotOpacity.addEventListener('input', () => {
        const opacity = dotOpacity.value;
        dotOpacityValue.textContent = opacity;
        dot.style.backgroundColor = `rgba(255,0,0,${opacity})`;
    });

    radiusInput.addEventListener("input", updateCircle);
    opacityInput.addEventListener("input", updateCircle);
    updateCircle();

    const thetaInput = document.getElementById('theta');

    function getRotationAmount() {
        const rotationAmount = parseFloat(thetaInput.value);
        const startAngle = parseFloat(angleInput.value);
        return { rotationAmount, startAngle };
    }

    function animate() {
        if (Math.abs(currentRotation - rotationTarget) > 0.1) {
            currentRotation += rotationSpeed;
            circle.style.transform = `rotate(${-currentRotation}deg)`;
            const normalizedRotation = ((currentRotation % 360) + 360) % 360;
            angleInput.value = normalizedRotation.toFixed(2);
            angleValue.textContent = normalizedRotation.toFixed(0);
            updateDotPosition(normalizedRotation, radiusInput.value);
            updateThetaValue(normalizedRotation);
            animationId = requestAnimationFrame(animate);
        } else {
            isAnimating = false;
            const finalRotation = ((currentRotation % 360) + 360) % 360;
            angleInput.value = finalRotation.toFixed(2);
            angleValue.textContent = finalRotation.toFixed(0);
            updateDotPosition(finalRotation, radiusInput.value);
            updateThetaValue(finalRotation);
            updatePositionEuler();
            rotationSpeed = 0;
            cancelAnimationFrame(animationId);
            animationId = null;
        }
    }

    function updateThetaValue(angle) {
        if (isAnimating) {
            tempThetaValue.textContent = `θ = ${angle.toFixed(2)}`;
        } else {
            tempThetaValue.innerHTML = `\\(\\theta = ${angle.toFixed(2)}\\)`;
            MathJax.typeset([tempThetaValue]);
        }
    }

    function startRotation(factor) {
        isAnimating = true;
        const { rotationAmount, startAngle } = getRotationAmount();
        currentRotation = startAngle;
        rotationTarget = currentRotation + rotationAmount * factor;
        rotationSpeed = rotationAmount * factor / 60;
        const finalRotation = ((rotationTarget % 360) + 360) % 360;
        updateDotPosition(finalRotation, radiusInput.value);
        angleValue.textContent = finalRotation.toFixed(0);
        circle.style.transform = `rotate(${-currentRotation}deg)`;
        if (!animationId) {
            animationId = requestAnimationFrame(animate);
        }
    }

    function updatePositionEuler() {
        const theta = thetaInput.value;
        const angle = angleInput.value;
        const radius = radiusInput.value;
        
        // Calculate the Euler formula values
        const angleRadians = angle * (Math.PI / 180);
        const thetaRadians = theta * (Math.PI / 180);
        
        // Calculate e^(iθ) = cos(θ) + i*sin(θ)
        const realPart = Math.cos(thetaRadians);
        const imagPart = Math.sin(thetaRadians);
        
        // Calculate position
        const posX = (radius / 10) * Math.cos(angleRadians);
        const posY = (radius / 10) * Math.sin(angleRadians);
        
        // Multiply position by e^(iθ)
        // (a + bi)(c + di) = (ac - bd) + (ad + bc)i
        const resultReal = posX * realPart - posY * imagPart;
        const resultImag = posX * imagPart + posY * realPart;
        
        // Update the Euler value display
        eulerValue.innerHTML = `(Position) \\cdot e^{i\\theta} = ${resultReal.toFixed(2)} + ${resultImag.toFixed(2)}i`;
        thetaValue.innerHTML = `\\(\\theta = ${parseFloat(theta).toFixed(2)}\\)`;
        
        // Typeset the MathJax
        MathJax.typeset([eulerValue, thetaValue]);
    }

    thetaInput.addEventListener('input', updatePositionEuler);
    
    rotation.addEventListener('click', () => {
        startRotation(1);  // Positive for clockwise rotation
    });

    counterRotation.addEventListener('click', () => {
        startRotation(-1);  // Negative for counter-clockwise rotation
    });
    
    // Call updatePositionEuler once at load to initialize values
    updatePositionEuler();
    
    // Set initial values
    updateDotPosition(parseFloat(angleInput.value), parseFloat(radiusInput.value));
});