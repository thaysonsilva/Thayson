self.addEventListener('push', event => {
    const data = event.data.text();
    event.waitUntil(
        self.registration.showNotification("Nova mensagem", {
            body: data,
            actions:[{action:"responder", title:"Responder"}]
        })
    );
});

self.addEventListener('notificationclick', event => {
    if(event.action === "responder") {
        clients.openWindow("/responder?username=usuario");
    }
    event.notification.close();
});