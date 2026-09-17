
def missing_config_variables(instance):
    if instance is None or not instance.pk or not instance.config_id:
        return []

    existing_variable_ids = instance.variable_instances.values_list(
        "variable_id", flat=True
    )
    return instance.config.variables.exclude(pk__in=existing_variable_ids)
