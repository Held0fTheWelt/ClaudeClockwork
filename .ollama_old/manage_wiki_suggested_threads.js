```javascript
function renderSuggestedThreadsList(items) {
    var listEl = $("manage-wiki-suggested-threads-list");
    if (!listEl) return;
    while (listEl.firstChild) listEl.removeChild(listEl.firstChild);
    if (!items || items.length === 0) {
        var empty = document.createTextNode("No suggestions.");
        listEl.appendChild(empty);
        return;
    }
    var ul = document.createElement("ul");
    ul.className = "manage-suggested-threads-ul";
    items.forEach(function(t) {
        if (!t) return;
        var li = document.createElement("li");
        li.className = "manage-suggested-thread-item";
        var span = document.createElement("span");
        span.textContent = (t.title || ("Thread #" + t.id)) + " (#" + t.id + ")";
        li.appendChild(span);
        var addBtn = document.createElement("button");
        addBtn.type = "button";
        addBtn.className = "btn btn-ghost btn-sm";
        addBtn.textContent = "Add as related";
        addBtn.setAttribute("aria-label", "Add this suggested thread as related");
        (function(tid) {
            addBtn.addEventListener("click", function() {
                onRelatedThreadAdd(tid);
            });
        }(t.id));
        li.appendChild(addBtn);
        ul.appendChild(li);
    });
    listEl.appendChild(ul);
}

function fetchSuggestedThreads() {
    var id = ($("manage-wiki-id") || {}).value;
    if (!id) return;
    apiRef("/api/v1/wiki/" + id + "/suggested-threads")
        .then(function(data) {
            renderSuggestedThreadsList(data.items || []);
        })
        .catch(function() {
            var listEl = $("manage-wiki-suggested-threads-list");
            if (listEl) listEl.textContent = "Failed to load suggested threads.";
        });
}

function onRelatedThreadAdd(threadIdFromSuggested) {
    var id = ($("manage-wiki-id") || {}).value;
    if (!id) return;
    apiRef("/api/v1/wiki/" + id + "/related-threads", {
        method: "POST",
        body: JSON.stringify({ thread_id: threadIdFromSuggested })
    })
    .then(function() {
        showWikiFormSuccess("Thread added successfully.");
        fetchSuggestedThreads();
    })
    .catch(function() {
        showWikiFormError("Failed to add thread.");
    });
}
```