from pydantic import BaseModel, ConfigDict, Field

from analysis.weekly_labels import Label


class WeeklyLabelItem(BaseModel):
    """One food component, or one always-together group, and its label. Never carries a confidence number."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="Component slug, or merge group id when is_group is true")
    display_name: str
    is_group: bool
    member_slugs: list[str] = Field(description="Component slugs in the group, or just this component")
    label: Label


class WeeklyResultsResponse(BaseModel):
    """The current user's labels, grouped by label. Only components they have eaten at a meaningful amount appear."""

    model_config = ConfigDict(from_attributes=True)

    likely_trigger: list[WeeklyLabelItem] = []
    still_learning: list[WeeklyLabelItem] = []
    looks_fine: list[WeeklyLabelItem] = []
    no_clear_pattern: bool = Field(
        default=False, description="True when at least 60% look fine and nothing is close to a trigger"
    )
