```mermaid
{% raw %}
%%{init: {"flowchart": {"htmlLabels": false}} }%%
{% endraw %}

flowchart LR
  
    {% for table in collection.tables -%}
        {{ table }}["{{ table }}"]
    {% endfor %}

    {% for link in collection.links -%}
        {{ link.source_table_sid }} --> {{ link.target_table_sid }}
    {% endfor %}    

```