{% with res=resolution.resolution_title id=resolution.resolution_id %}
# {% if res %} {{ res }} {% else %} Uchwała: {{ id }} {% endif %}
{% endwith %}

{{ resulution.resolution_text }}

## Metadane

* **Organ podejmujący**: {{ resulution.unit.name }}
* **Sygnatura uchwały**: {{ resolution.resolution_id }}
* **Data podjęcia uchwały**: {{ resolution.date_voting_finished.isoformat }}
{% if resulution.resolution_passed %}* **Uchwała nie została przegłosowana** {% endif %}

## Wyniki głosowania

{% for label, count in resolution.voting_results %}
* **{{ label }}: ** {{ count }}{% endfor %}

{% if resolution.public %}

## Oddane głosy 

{% for vote in resolution.votes.all %}
* **{{ vote.voter.get_full_name }}**: {{ vote.get_vote_type_display }}{% endfor %}

{% endif %}
