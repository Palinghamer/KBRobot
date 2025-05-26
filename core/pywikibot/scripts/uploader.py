import pywikibot
import pandas as pd
import re
import time
from datetime import datetime

class WikidataUploader:
    def __init__(self, site, property_map, source_map, logger):
        self.site = site
        self.repo = site.data_repository()
        self.property_map = property_map
        self.source_map = source_map
        self.logger = logger
        self.stats = {
            "processed": 0,
            "created": 0,
            "skipped": 0,
            "claims_added": 0,
            "claims_skipped": 0,
            "sources_added": 0,
            "sources_skipped": 0
        }
        self.change_log = []

    def log_with_item(self, title, item_id=None, level="warning", message=""):
        prefix = f"[{item_id if item_id else 'no QID'}] {title} -"
        full_message = f"{prefix} {message}"
        getattr(self.logger, level)(full_message)

    def get_items(self, item_title):
        from pywikibot.data import api
        params = {
            "action": "wbsearchentities",
            "format": "json",
            "language": "en",
            "type": "item",
            "search": item_title
        }
        request = api.Request(site=self.site, parameters=params)
        return request.submit()

    def check_item_exists(self, item_title):
        search_results = self.get_items(item_title)
        if "search" in search_results:
            for result in search_results["search"]:
                if result.get("label", "").strip().lower() == item_title.strip().lower():
                    return result["id"]
        return None

    def create_item(self, label_dict):
        new_item = pywikibot.ItemPage(self.site)
        new_item.editLabels(labels=label_dict, summary="Creating a new item.", bot=True)
        new_id = new_item.getID()
        self.change_log.append({
            "Title": label_dict.get("en", ""),
            "QID": new_id,
            "Type": "Item",
            "Action": "Created",
            "Property": "",
            "Value": ""
        })
        return new_id

    def wait_for_item_to_be_searchable(self, label, created_id, max_wait=600, interval=60):
        waited = 0
        while waited < max_wait:
            found_id = self.check_item_exists(label)
            if found_id:
                self.log_with_item(label, created_id, "warning", f"Item is now indexed as {found_id}. Continuing.")
                return True
            self.log_with_item(label, created_id, "warning", f"Item not indexed. Waiting {interval} seconds...")
            time.sleep(interval)
            waited += interval
        self.log_with_item(label, created_id, "warning", "Item not indexed after timeout.")
        return False

    def check_and_create_item(self, title):
        item_id = self.check_item_exists(title)
        if item_id:
            self.log_with_item(title, item_id, "warning", "Item already exists.")
            return None
        labels = {"en": title}
        new_id = self.create_item(labels)
        self.log_with_item(title, new_id, "warning", f"Created new item {new_id}.")
        self.wait_for_item_to_be_searchable(title, new_id)
        return new_id

    def claim_already_exists(self, item, prop, target_value):
        existing_claims = item.claims.get(prop, [])
        for claim in existing_claims:
            if isinstance(target_value, pywikibot.ItemPage) and claim.getTarget().id == target_value.id:
                return True
            elif isinstance(target_value, str) and claim.getTarget() == target_value:
                return True
            elif isinstance(target_value, pywikibot.WbTime) and claim.getTarget().toTimestr() == target_value.toTimestr():
                return True
        return False

    def set_descriptions(self, item_id, row):
        item = pywikibot.ItemPage(self.repo, item_id)
        item.get(force=True)
        title = row.get("Title", "")
        new_descriptions = {}

        for col in row.index:
            match = re.match(r"[Dd]escription_(\w+)", col)
            if match:
                lang = match.group(1)
                new_desc = str(row[col]).strip()
                if pd.notna(new_desc) and new_desc:
                    current_desc = item.descriptions.get(lang, "")
                    if new_desc != current_desc:
                        new_descriptions[lang] = new_desc

        if new_descriptions:
            try:
                item.editDescriptions(new_descriptions, summary="Updating item descriptions.", bot=True)
                self.log_with_item(title, item_id, "info", f"Descriptions updated: {new_descriptions}")
                for lang, desc in new_descriptions.items():
                    self.change_log.append({
                        "Title": title,
                        "QID": item_id,
                        "Type": "Description",
                        "Action": "Updated",
                        "Property": f"description_{lang}",
                        "Value": desc
                    })
            except Exception as e:
                self.log_with_item(title, item_id, "error", f"Failed to update descriptions: {e}")
        else:
            self.log_with_item(title, item_id, "warning", "No description updates needed.")

    def add_claims(self, item_id, row):
        item = pywikibot.ItemPage(self.repo, item_id)
        item.get()
        title = row.get("Title", "")

        for col in row.index:
            if col in ["Title", "QID"] or col not in self.property_map or pd.isna(row[col]):
                continue

            mapping = self.property_map[col]
            prop = mapping["property"]
            val_type = mapping["type"]
            values = [v.strip() for v in str(row[col]).split(";") if v.strip()]

            for value in values:
                try:
                    if val_type == "item":
                        match = re.search(r"Q\d+", value)
                        if match:
                            target = pywikibot.ItemPage(self.repo, match.group(0))
                            target.get()
                            if self.claim_already_exists(item, prop, target):
                                self.stats["claims_skipped"] += 1
                                self.change_log.append({
                                    "Title": title,
                                    "QID": item_id,
                                    "Type": "Claim",
                                    "Action": "Skipped",
                                    "Property": prop,
                                    "Value": target.id
                                })
                                continue
                            claim = pywikibot.Claim(self.repo, prop)
                            claim.setTarget(target)
                            item.addClaim(claim, bot=True, summary=f"Adding claim {prop} -> {target.id}")
                            self.stats["claims_added"] += 1
                            self.change_log.append({
                                "Title": title,
                                "QID": item_id,
                                "Type": "Claim",
                                "Action": "Added",
                                "Property": prop,
                                "Value": target.id
                            })

                    elif val_type == "string":
                        if self.claim_already_exists(item, prop, value):
                            self.stats["claims_skipped"] += 1
                            self.change_log.append({
                                "Title": title,
                                "QID": item_id,
                                "Type": "Claim",
                                "Action": "Skipped",
                                "Property": prop,
                                "Value": value
                            })
                            continue
                        claim = pywikibot.Claim(self.repo, prop)
                        claim.setTarget(value)
                        item.addClaim(claim, bot=True, summary=f"Adding claim {prop} -> {value}")
                        self.stats["claims_added"] += 1
                        self.change_log.append({
                            "Title": title,
                            "QID": item_id,
                            "Type": "Claim",
                            "Action": "Added",
                            "Property": prop,
                            "Value": value
                        })

                    elif val_type == "date":
                        parsed = pd.to_datetime(value, errors="coerce")
                        if pd.notna(parsed):
                            date_target = pywikibot.WbTime(year=parsed.year, month=parsed.month, day=parsed.day)
                            if self.claim_already_exists(item, prop, date_target):
                                self.stats["claims_skipped"] += 1
                                self.change_log.append({
                                    "Title": title,
                                    "QID": item_id,
                                    "Type": "Claim",
                                    "Action": "Skipped",
                                    "Property": prop,
                                    "Value": str(parsed.date())
                                })
                                continue
                            dateclaim = pywikibot.Claim(self.repo, prop)
                            dateclaim.setTarget(date_target)
                            item.addClaim(dateclaim, bot=True, summary=f"Adding date claim {prop} -> {parsed.date()}")
                            self.stats["claims_added"] += 1
                            self.change_log.append({
                                "Title": title,
                                "QID": item_id,
                                "Type": "Claim",
                                "Action": "Added",
                                "Property": prop,
                                "Value": str(parsed.date())
                            })
                except Exception as e:
                    self.log_with_item(title, item_id, "error", f"Error adding claim {prop}: {e}")

    def add_sources(self, item_id, row):
        item = pywikibot.ItemPage(self.repo, item_id)
        item.get()
        title = row.get("Title", "")

        for prop, claims in item.claims.items():
            for claim in claims:
                try:
                    existing_sources = claim.getSources()
                except Exception as e:
                    self.log_with_item(title, item_id, "warning", f"Couldn't get sources: {e}")
                    continue

                for source_col, source_info in self.source_map.items():
                    if "targets" in source_info and prop not in source_info["targets"]:
                        continue

                    source_prop = source_info["property"]
                    source_type = source_info["type"]
                    raw_value = row.get(source_col)

                    if pd.isna(raw_value):
                        continue

                    for val in str(raw_value).split(";"):
                        val = val.strip()
                        if not val:
                            continue
                        try:
                            source_claim = pywikibot.Claim(self.repo, source_prop, is_reference=True)

                            if source_type == "item":
                                match = re.search(r"Q\d+", val)
                                if match:
                                    target = pywikibot.ItemPage(self.repo, match.group(0))
                                    target.get()
                                    source_claim.setTarget(target)
                                else:
                                    continue

                            elif source_type == "string":
                                source_claim.setTarget(val)

                            elif source_type == "date":
                                dt = pd.to_datetime(val, errors="coerce")
                                if pd.isna(dt):
                                    continue
                                date_target = pywikibot.WbTime(year=dt.year, month=dt.month, day=dt.day)
                                source_claim.setTarget(date_target)

                            if any(
                                source_claim.getID() in existing and
                                any(source_claim.getTarget() == existing_claim.getTarget() for existing_claim in existing[source_claim.getID()])
                                for existing in existing_sources
                            ):
                                self.stats["sources_skipped"] += 1
                                self.change_log.append({
                                    "Title": title,
                                    "QID": item_id,
                                    "Type": "Source",
                                    "Action": "Skipped",
                                    "Property": source_prop,
                                    "Value": str(source_claim.getTarget())
                                })
                                continue

                            claim.addSources([source_claim], summary=f"Adding source {source_claim.getID()}")
                            self.stats["sources_added"] += 1
                            self.change_log.append({
                                "Title": title,
                                "QID": item_id,
                                "Type": "Source",
                                "Action": "Added",
                                "Property": source_prop,
                                "Value": str(source_claim.getTarget())
                            })
                        except Exception as e:
                            self.log_with_item(title, item_id, "error", f"Source error: {e}")

    def upload_from_dataframe(self, df, csv_path):
        for idx, row in df.iterrows():
            self.stats["processed"] += 1
            qid = str(row.get("QID")).strip() if "QID" in row else None
            title = row.get("Title", "")

            if not qid or not re.match(r"^Q\d+$", qid):
                qid = self.check_and_create_item(title)
                if not qid:
                    self.stats["skipped"] += 1
                    self.log_with_item(title, None, "warning", "No QID, skipping.")
                    continue
                self.stats["created"] += 1
                df.at[idx, "QID"] = qid
                df.to_csv(csv_path, index=False)

            self.add_claims(qid, row)
            self.set_descriptions(qid, row)
            self.add_sources(qid, row)


    def save_summary_csv(self, filename=None):
        import os

        # Go from scripts/ → core/ → pywiki/
        script_dir = os.path.dirname(os.path.abspath(__file__))
        pywiki_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
        logs_dir = os.path.join(pywiki_root, "logs")
        os.makedirs(logs_dir, exist_ok=True)

        # Default to timestamped filename if none provided
        if filename is None:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"summary_log_{timestamp}.csv"

        full_path = os.path.join(logs_dir, filename)

        if not self.change_log:
            self.logger.info("No changes to save.")
            return

        import pandas as pd
        df = pd.DataFrame(self.change_log)
        df.to_csv(full_path, index=False)
        self.logger.info(f"Saved summary CSV: {full_path}")
