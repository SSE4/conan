{% macro iterate_configs(var_config, action) -%}
    {% for it, values in var_config.items() -%}
        {%- set genexpr = namespace(str='') %}
        {%- for conf, value in values -%}
            {%- set genexpr.str = genexpr.str +
                                  '$<IF:$<CONFIG:' + conf + '>,"' + value|string + '",' %}
            {%- if loop.last %}{% set genexpr.str = genexpr.str + '""' -%}{%- endif -%}
        {%- endfor -%}
        {% for i in range(values|count) %}{%- set genexpr.str = genexpr.str + '>' %}{%- endfor -%}
        {% if action=='set' %}
set({{ it }} {{ genexpr.str }})
        {% elif action=='add_definitions' %}
add_definitions(-D{{ it }}={{ genexpr.str }})
        {% endif %}
    {%- endfor %}
{% endmacro %}
