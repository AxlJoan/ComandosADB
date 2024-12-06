document.getElementById('comandoForm').addEventListener('submit', function(event) {
    event.preventDefault();  // Evita que se recargue la página

    // Obtener los valores del formulario
    const link = document.getElementById('link').value;
    const comando = document.getElementById('comando').value;
    const option = document.getElementById('option').value;
    const temporizador = document.getElementById('temporizador').value;

    // Crear el objeto con los datos a enviar
    const data = {
        link: link,
        comando: comando,
        option: option,
        temporizador: temporizador
    };

    // Realizar la solicitud POST al servidor Flask
    fetch('/comando', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        // Mostrar el resultado en el div de resultado
        const resultadoDiv = document.getElementById('resultado');
        if (result.message) {
            resultadoDiv.innerHTML = `<p style="color: green;">${result.message}</p>`;
        } else if (result.error) {
            resultadoDiv.innerHTML = `<p style="color: red;">${result.error}</p>`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('resultado').innerHTML = `<p style="color: red;">Ocurrió un error al enviar el comando.</p>`;
    });
});
