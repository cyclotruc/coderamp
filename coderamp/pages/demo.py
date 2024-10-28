import reflex as rx

from ..coderamp_lib.coderamp import Coderamp
from rxconfig import CODERAMP_DOMAIN

from reflex_monaco import monaco

class DemoState(rx.State):
    ready: bool = False
    name: str = ""
    url: str = ""
    ports: str = ""
    active: bool = False
    id: str = ""
    created_at: str = ""
    cpu: str = ""
    memory: str = ""

    def get_config(self):
        print("Getting config//" * 10)
        try:
            ramp = Coderamp.select().where(Coderamp.slug == "evidence_demo").first()
            print(ramp, ramp.name)
            if ramp:
                self.name = ramp.name
                self.url = ramp.magic_url
                self.ports = ramp.ports
                self.cpu = "4"
                self.memory = "8"
                self.id = ramp.uuid
                self.active = ramp.ready
                self.created_at = ramp.created_at
                self.ready = True

        except Exception as e:
            print(e)


def port_badge(port: str) -> rx.Component:
    return rx.badge(port)


@rx.page(route="/demo", on_load=DemoState.get_config)
def demo() -> rx.Component:
    return (
        rx.center(
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.image(
                            src="https://raw.githubusercontent.com/evidence-dev/media-kit/refs/heads/main/png/logo-round-black-on-white.png",
                            alt="My Icon",
                            width="50px",
                            height="50px",
                        ),
                        rx.heading("Evidence.dev"),
                    ),
                    rx.spacer(),
                    rx.hstack(
                        monaco(
                            default_language="markdown",
                            default_value='''---
title: Welcome to Evidence
---

<Details title='How to edit this page'>

  This page can be found in your project at `/pages/index.md`. Make a change to the markdown file and save it to see the change take effect in your browser.
</Details>

```sql categories
  select
      category
  from needful_things.orders
  group by category
```

<Dropdown data={categories} name=category value=category>
    <DropdownOption value="%" valueLabel="All Categories"/>
</Dropdown>

<Dropdown name=year>
    <DropdownOption value=% valueLabel="All Years"/>
    <DropdownOption value=2019/>
    <DropdownOption value=2020/>
    <DropdownOption value=2021/>
</Dropdown>

```sql orders_by_category
  select 
      date_trunc('month', order_datetime) as month,
      sum(sales) as sales_usd,
      category
  from needful_things.orders
  where category like '${inputs.category.value}'
  and date_part('year', order_datetime) like '${inputs.year.value}'
  group by all
  order by sales_usd desc
```

<BarChart
    data={orders_by_category}
    title="Sales by Month, {inputs.category.label}"
    x=month
    y=sales_usd
    series=category
/>

## What's Next?
- [Connect your data sources](settings)
- Edit/add markdown files in the `pages` folder
- Deploy your project with [Evidence Cloud](https://evidence.dev/cloud)

## Get Support
- Message us on [Slack](https://slack.evidence.dev/)
- Read the [Docs](https://docs.evidence.dev/)
- Open an issue on [Github](https://github.com/evidence-dev/evidence)''',
                            height='700px',
                            width='600px',
                        ),
                        rx.card(
                            rx.data_list.root(
                                rx.data_list.item(
                                    rx.data_list.label("Name"),
                                    rx.data_list.value(DemoState.name),
                                ),
                                rx.data_list.item(
                                    rx.data_list.label("Ports"),
                                    rx.data_list.value(
                                        rx.foreach(DemoState.ports.split(","), port_badge)
                                    ),
                                ),
                                rx.data_list.item(
                                    rx.data_list.label("Documentation"),
                                    rx.data_list.value(
                                        rx.link(
                                            "Install Evidence",
                                            href="https://docs.evidence.dev/install-evidence/",
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                    rx.vstack(
                        rx.text(
                            "This button will open a new vscode instance with the Evidence"
                        ),
                        rx.button(
                            "Open Evidence",
                            on_click=rx.redirect(
                                f"https://{CODERAMP_DOMAIN}/new?id=evidence_demo"
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )
