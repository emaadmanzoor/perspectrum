from webapp.models import *
import datetime
import json

TIMEOUT_IDLE_MINUTE = 60

_TIMEOUT_IDLE_MINUTE = datetime.timedelta(minutes=TIMEOUT_IDLE_MINUTE)


def clean_paraphrase_idle_sessions():
    sessions = ParaphraseHITSession.objects.filter(job_complete=0, finished_jobs="[]")
    for s in sessions.iterator():
        last_access_time = s.last_start_time
        time_now = datetime.datetime.now(datetime.timezone.utc)
        elapsed = time_now - last_access_time
        if elapsed > _TIMEOUT_IDLE_MINUTE:
            jobs = json.loads(s.jobs)
            decrease_paraphrase_assign_counts(jobs)
            s.delete()


def increment_paraphrase_assign_counts(eb_ids):
    """
    increase by assignment counts of the claim ids by 1
    :param claim_ids:
    :return:
    """
    return _offset_paraphrase_assign_counts(eb_ids, 1)


def decrease_paraphrase_assign_counts(eb_ids):
    """
    decrease by assignment counts of the claim ids by 1
    :param claim_ids:
    :return:
    """
    return _offset_paraphrase_assign_counts(eb_ids, -1)


def _offset_paraphrase_assign_counts(eb_ids, offset):
    for cid in eb_ids:
        eb = ParaphraseBatch.objects.get(id=cid)
        target = eb.assign_counts + offset
        if target >= 0:
            eb.assign_counts = target
        else:
            eb.assign_counts = 0

        eb.save()


def get_all_finished_batches(username):
    _jobs = ParaphraseHITSession.objects.filter(username=username).values_list("jobs", flat=True)
    jobs = []
    for j in _jobs:
        jobs += json.loads(j)

    return jobs