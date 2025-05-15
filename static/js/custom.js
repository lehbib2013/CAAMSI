document.getElementById('ajouterFournisseurForm').addEventListener('submit', function (event) {
    event.preventDefault();

    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());

    fetch('/fournisseurs', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
        .then(response => {
            if (response.ok) {
                alert('Fournisseur ajouté avec succès!');
                location.reload();
            } else {
                alert('Erreur lors de l\'ajout du fournisseur.');
            }
        })
        .catch(error => console.error('Error:', error));
});
