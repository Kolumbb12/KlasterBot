function toggleAgentStatus(agentId) {
    // Пример кода для AJAX-запроса, который изменяет статус агента
    fetch(`/toggle_agent_status/${agentId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id: agentId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert("Не удалось изменить статус агента.");
        }
    })
    .catch(error => console.error('Ошибка:', error));
}
