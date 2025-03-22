 const canvas = document.getElementById('drawing-canvas');
 const ctx = canvas.getContext('2d');
 ctx.strokeStyle = 'white';
 ctx.lineWidth = 15;
 ctx.lineCap = 'round';
 
 // Drawing state
 let isDrawing = false;
 let lastX = 0;
 let lastY = 0;
 
 canvas.addEventListener('mousedown', startDrawing);
 canvas.addEventListener('mousemove', draw);
 canvas.addEventListener('mouseup', stopDrawing);
 canvas.addEventListener('mouseout', stopDrawing);
 
 canvas.addEventListener('touchstart', handleTouch);
 canvas.addEventListener('touchmove', handleTouch);
 canvas.addEventListener('touchend', stopDrawing);
 
 function handleTouch(e) {
     e.preventDefault();
     const touch = e.touches[0];
     const mouseEvent = new MouseEvent(e.type === 'touchstart' ? 'mousedown' : 'mousemove', {
         clientX: touch.clientX,
         clientY: touch.clientY
     });
     canvas.dispatchEvent(mouseEvent);
 }
 
 function startDrawing(e) {
     isDrawing = true;
     [lastX, lastY] = [e.offsetX, e.offsetY];
 }
 
 function draw(e) {
     if (!isDrawing) return;
     
     ctx.beginPath();
     ctx.moveTo(lastX, lastY);
     ctx.lineTo(e.offsetX, e.offsetY);
     ctx.stroke();
     
     [lastX, lastY] = [e.offsetX, e.offsetY];
     
     document.getElementById('result-container').classList.add('hidden');
 }
 
 function stopDrawing() {
     isDrawing = false;
 }
 
 function clearCanvas() {
     ctx.fillStyle = 'black';
     ctx.fillRect(0, 0, canvas.width, canvas.height);
     document.getElementById('result-container').classList.add('hidden');
 }
 
 async function classifyDigit() {
     const imageData = canvas.toDataURL('image/png');
     
     document.getElementById('status').textContent = 'Classifying...';
     
     try {
         const response = await fetch('/api/classify', {
             method: 'POST',
             headers: {
                 'Content-Type': 'application/json'
             },
             body: JSON.stringify({
                 image: imageData
             })
         });
         
         if (!response.ok) {
             throw new Error('Server error');
         }
         
         const result = await response.json();
         
         document.getElementById('prediction').textContent = `Predicted Digit: ${result.predicted_digit}`;
         document.getElementById('result-container').classList.remove('hidden');
         
         for (let i = 0; i < 10; i++) {
             const probability = result.probabilities[i] * 100;
             document.getElementById(`bar-${i}`).style.height = `${probability}%`;
             document.getElementById(`value-${i}`).textContent = `${probability.toFixed(1)}%`;
         }
         
         document.getElementById('status').textContent = 'Classification complete!';
         
     } catch (error) {
         console.error('Error classifying digit:', error);
         document.getElementById('status').textContent = 'Error: Could not classify the digit. Please try again.';
     }
 }
 
 document.getElementById('clear-button').addEventListener('click', clearCanvas);
 document.getElementById('classify-button').addEventListener('click', classifyDigit);
 
 clearCanvas();