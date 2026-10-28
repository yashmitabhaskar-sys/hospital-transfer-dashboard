import streamlit as st

from database import (
    create_table,
    add_referral,
    get_referrals,
    update_status,
    delete_referral,
    get_events,
    add_patient_upload,
    get_patient_uploads,
    get_all_patient_uploads,
    get_upload_file,
    mark_upload_reviewed,
    add_medical_history,
    get_medical_history,
    delete_medical_history,
)

st.set_page_config(
    page_title="ReferralLoop",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

create_table()

# ---------- UI THEME ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --rl-ink: #1e293b;
    --rl-muted: #64748b;
    --rl-line: #e6eaf0;
    --rl-bg: #f6f8fb;
    --rl-blue: #2563eb;
    --rl-teal: #0f766e;
}
html, body, [class*="css"] {
    font-family: "DM Sans", sans-serif;
}
.stApp {
    background: #f6f8fb;
    color: #1e293b;
}
[data-testid="stHeader"] {
    background: rgba(246,248,251,.92);
}
.block-container {
    max-width: 1240px;
    padding-top: 1.7rem;
    padding-bottom: 3rem;
}
h1, h2, h3 {
    font-family: "Manrope", "DM Sans", sans-serif !important;
    color: #172033;
    letter-spacing: -.5px;
}
h1 { font-weight: 800 !important; }
h2, h3 { font-weight: 750 !important; }
p, label, [data-testid="stMarkdownContainer"] {
    color: #334155;
}
[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e6eaf0;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.5rem;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e6eaf0;
    border-radius: 16px;
    padding: 1.1rem 1.2rem;
    box-shadow: 0 8px 28px rgba(24,39,75,.045);
}
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e6eaf0;
    border-radius: 16px;
    padding: 1.1rem 1.2rem;
    box-shadow: 0 8px 28px rgba(24,39,75,.045);
}
div[data-testid="stMetricLabel"] p {
    color: #64748b !important;
    font-size: .8rem;
}
div[data-testid="stMetricValue"] {
    color: #172033;
    font-family: "Manrope", sans-serif;
    font-weight: 800;
}
.stButton > button, .stDownloadButton > button, button[kind="primary"] {
    border-radius: 10px;
    border: 1px solid #dbe3ee;
    padding: .55rem 1rem;
    font-weight: 700;
    transition: all .15s ease;
}
.stButton > button[kind="primary"], button[kind="primary"] {
    background: linear-gradient(135deg,#2563eb,#0f766e);
    color: white;
    border: 0;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: #2563eb;
    color: #1d4ed8;
}
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea,
div[data-baseweb="select"] > div {
    border-radius: 10px !important;
    border-color: #dce3ec !important;
    background: #fff !important;
}
div[data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid #e6eaf0;
}
button[data-baseweb="tab"] {
    border-radius: 9px 9px 0 0;
    padding: .7rem 1rem;
    font-weight: 700;
}
div[data-testid="stAlert"] {
    border-radius: 12px;
}
/* High-contrast controls: readable labels in light and dark Streamlit themes */
.stButton > button,
.stDownloadButton > button,
div[data-testid="stFormSubmitButton"] > button,
div[data-testid="stPopover"] button {
    color: #172033 !important;
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    font-weight: 750 !important;
}
.stButton > button[kind="primary"],
div[data-testid="stFormSubmitButton"] > button[kind="primary"] {
    color: #ffffff !important;
    background: linear-gradient(135deg, #1d4ed8, #0f766e) !important;
    border: 0 !important;
}
.stButton > button:disabled,
.stDownloadButton > button:disabled {
    color: #64748b !important;
    background: #f1f5f9 !important;
}
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] div[role="combobox"] {
    color: #172033 !important;
    -webkit-text-fill-color: #172033 !important;
    background-color: #ffffff !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder {
    color: #64748b !important;
    -webkit-text-fill-color: #64748b !important;
}
[data-testid="stFileUploader"] section {
    background: #ffffff !important;
    border: 1px dashed #94a3b8 !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploader"] button {
    color: #172033 !important;
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
}
[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] span {
    color: #334155 !important;
}
.rl-brand {
    display:flex; align-items:center; gap:12px; margin-bottom:1.25rem;
}
.rl-mark {
    width:46px;height:46px;border-radius:14px;
    display:flex;align-items:center;justify-content:center;
    background:linear-gradient(135deg,#2563eb,#0f766e);
    color:white;font-size:23px;font-weight:800;
    box-shadow:0 7px 18px #2563eb30;
}
.rl-name {font:800 25px Manrope,sans-serif; letter-spacing:-.8px; color:#172033;}
.rl-name span {color:#2563eb;}
.rl-sub {color:#64748b;font-size:12px;margin-top:1px;}
.rl-eyebrow {font-size:10px;letter-spacing:1.5px;font-weight:800;color:#2563eb;text-transform:uppercase;}
.rl-lead {color:#64748b;line-height:1.7;font-size:15px;}
.rl-chip {display:inline-block;border-radius:99px;background:#eaf2ff;color:#2459bf;padding:5px 10px;font-size:11px;font-weight:800;}
.rl-footer {text-align:center;color:#94a3b8;font-size:11px;padding:2rem 0 .5rem;}
@media (max-width: 700px) {
  .block-container {padding-left:1rem;padding-right:1rem;}
  .rl-name {font-size:22px;}
}
</style>
""", unsafe_allow_html=True)


def brand():
    st.markdown("""
    <div class="rl-brand">
      <div class="rl-mark">R</div>
      <div>
        <div class="rl-name">Referral<span>Loop</span></div>
        <div class="rl-sub">Care that stays connected</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def show_history(referral_id):
    events = get_events(referral_id)
    if not events:
        st.caption("No handover history recorded yet.")
        return
    for event_status, event_time, details in events:
        st.markdown(f"**{event_status}** · {event_time}")
        if details:
            st.caption(details)


def show_official_history(patient_id, allow_edit=False):
    history = get_medical_history(patient_id)
    if not history:
        st.info("No official medical-history entries yet.")
        return

    for item in history:
        history_id, _, entry, doctor_name, created_at = item
        with st.container(border=True):
            st.markdown(f"**{entry}**")
            st.caption(f"Recorded by {doctor_name} · {created_at}")
            if allow_edit:
                key = f"delete_history_{history_id}"
                if st.button("Delete entry", key=key):
                    st.session_state.pending_history_delete = history_id
                    st.rerun()
                if st.session_state.get("pending_history_delete") == history_id:
                    st.warning("Confirm deletion of this history entry.")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Confirm delete", key=f"confirm_history_{history_id}"):
                            delete_medical_history(history_id)
                            st.session_state.pending_history_delete = None
                            st.rerun()
                    with c2:
                        if st.button("Cancel", key=f"cancel_history_{history_id}"):
                            st.session_state.pending_history_delete = None
                            st.rerun()


def show_referral(referral, hospital_mode=False, doctor_mode=False):
    (
        referral_id, patient_id, sending, receiving, reason, summary,
        status, documents_provided, documents_required
    ) = referral

    with st.container(border=True):
        left, right = st.columns([4, 1])
        with left:
            st.markdown("### Referral details")
            st.caption(f"Patient ID · {patient_id}")
        with right:
            colors = {
                "Sent": "🔵", "Received": "🟡", "Accepted": "🟢",
                "Completed": "✅", "Rejected": "🔴"
            }
            st.markdown(f"**{colors.get(status, '⚪')} {status}**")

        a, b = st.columns(2)
        with a:
            st.markdown("**Sending hospital**")
            st.write(sending)
        with b:
            st.markdown("**Receiving hospital**")
            st.write(receiving)

        st.markdown("**Reason for referral**")
        st.write(reason)
        st.markdown("**Medical summary**")
        st.write(summary or "Not provided")

        docs1, docs2 = st.columns(2)
        with docs1:
            st.markdown("**📎 Documents provided**")
            st.write(documents_provided or "None listed")
        with docs2:
            st.markdown("**📋 Documents required**")
            st.write(documents_required or "None listed")

        can_act = hospital_mode and receiving == st.session_state.user["hospital"]
        if can_act:
            st.markdown("---")
            if status == "Sent":
                if st.button("Acknowledge receipt", key=f"receive_{referral_id}", type="primary"):
                    update_status(referral_id, "Received")
                    st.rerun()
            elif status == "Received":
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Accept handover", key=f"accept_{referral_id}", type="primary"):
                        update_status(referral_id, "Accepted")
                        st.rerun()
                with c2:
                    with st.popover("Reject referral"):
                        rejection_reason = st.text_area("Reason for rejection", key=f"reject_reason_{referral_id}")
                        if st.button("Confirm rejection", key=f"confirm_reject_{referral_id}"):
                            if not rejection_reason.strip():
                                st.error("Enter a rejection reason.")
                            elif update_status(referral_id, "Rejected", rejection_reason.strip()):
                                st.success("Referral rejected.")
                                st.rerun()
                            else:
                                st.error("Could not update referral.")
            elif status == "Accepted":
                if st.button("Mark outcome documented", key=f"complete_{referral_id}", type="primary"):
                    update_status(referral_id, "Completed")
                    st.rerun()

        if status == "Rejected":
            st.error("This referral was rejected.")
        elif status == "Completed":
            st.success("Referral workflow completed.")

        with st.expander("View handover timeline"):
            show_history(referral_id)

        if doctor_mode:
            if st.button("Delete referral", key=f"delete_referral_{referral_id}"):
                st.session_state.pending_delete = referral_id
                st.rerun()
            if st.session_state.get("pending_delete") == referral_id:
                st.warning("This permanently deletes the referral and its handover history.")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Confirm delete", key=f"confirm_delete_{referral_id}"):
                        delete_referral(referral_id)
                        st.session_state.pending_delete = None
                        st.rerun()
                with c2:
                    if st.button("Cancel", key=f"cancel_delete_{referral_id}"):
                        st.session_state.pending_delete = None
                        st.rerun()


# ---------- LOGIN SCREEN ----------
if "user" not in st.session_state:
    st.session_state.user = None
if "pending_delete" not in st.session_state:
    st.session_state.pending_delete = None
if "pending_history_delete" not in st.session_state:
    st.session_state.pending_history_delete = None

if st.session_state.user is None:
    brand()
    st.markdown('<div class="rl-eyebrow">CONNECTED CARE PLATFORM</div>', unsafe_allow_html=True)
    st.title("Care shouldn't lose its connection.")
    st.markdown(
        '<div class="rl-lead">One workspace for patient records, hospital referrals, and accountable handovers.</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        st.markdown("### Built for connected care")
        with st.container(border=True):
            st.markdown("#### ↗ Clear referral tracking")
            st.caption("Know what is pending, accepted, rejected, and completed.")
        with st.container(border=True):
            st.markdown("#### ▤ Patient documents and history")
            st.caption("Keep patient uploads separate from doctor-reviewed official history.")
        with st.container(border=True):
            st.markdown("#### ⌑ Role-specific dashboards")
            st.caption("Separate views for patients, hospitals, and doctors.")
        st.info("Hackathon demo only. Use fictional data, not real medical records.")

    with right:
        with st.container(border=True):
            st.markdown('<div class="rl-eyebrow">WELCOME</div>', unsafe_allow_html=True)
            st.subheader("Enter ReferralLoop")
            st.caption("Choose a demo account to open its dashboard.")
            with st.form("login_form"):
                account = st.selectbox(
                    "Account type",
                    ["Doctor", "Hospital A", "Hospital B", "Hospital C", "Patient"],
                )
                patient_id = ""
                if account == "Patient":
                    patient_id = st.text_input("Patient ID", placeholder="e.g. TEST-100")
                login_clicked = st.form_submit_button("Open dashboard", type="primary", use_container_width=True)

            if login_clicked:
                if account == "Patient" and not patient_id.strip():
                    st.error("Enter a patient ID.")
                elif account == "Doctor":
                    st.session_state.user = {"role": "Doctor"}
                    st.rerun()
                elif account.startswith("Hospital"):
                    st.session_state.user = {"role": "Hospital", "hospital": account}
                    st.rerun()
                else:
                    st.session_state.user = {"role": "Patient", "patient_id": patient_id.strip()}
                    st.rerun()
    st.markdown('<div class="rl-footer">ReferralLoop · Hackathon demo · Synthetic data only</div>', unsafe_allow_html=True)
    st.stop()


# ---------- APP SHELL ----------
user = st.session_state.user
role = user["role"]
with st.sidebar:
    brand()
    st.caption("WORKSPACE")
    st.markdown(f"**Signed in as {role}**")
    if role == "Hospital":
        st.caption(user["hospital"])
    elif role == "Patient":
        st.caption(f"Patient ID · {user['patient_id']}")
    st.divider()
    if st.button("Switch demo account", use_container_width=True):
        st.session_state.user = None
        st.rerun()
    st.markdown("---")
    st.caption("ReferralLoop")
    st.caption("Connected care, accountable handovers.")

if role == "Doctor":
    brand()
    st.markdown('<div class="rl-eyebrow">CLINICAL WORKSPACE</div>', unsafe_allow_html=True)
    st.title("Doctor dashboard")
    st.markdown('<div class="rl-lead">Manage referrals, review patient uploads, and maintain official medical history.</div>', unsafe_allow_html=True)

    referrals = get_referrals()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total referrals", len(referrals))
    m2.metric("Awaiting receipt", sum(r[6] == "Sent" for r in referrals))
    m3.metric("Rejected", sum(r[6] == "Rejected" for r in referrals))
    m4.metric("Completed", sum(r[6] == "Completed" for r in referrals))

    tab1, tab2, tab3 = st.tabs(["Referral register", "Medical history", "Patient uploads"])

    with tab1:
        with st.container(border=True):
            st.subheader("Create a referral")
            st.caption("Provide the handover details and list documents supplied or still needed.")
            with st.form("create_referral_form"):
                c1, c2 = st.columns(2)
                with c1:
                    patient_id = st.text_input("Patient ID")
                    sending = st.selectbox("Sending hospital", ["Hospital A", "Hospital B", "Hospital C"])
                    reason = st.text_input("Reason for referral")
                with c2:
                    receiving = st.selectbox("Receiving hospital", ["Hospital B", "Hospital A", "Hospital C"])
                    summary = st.text_area("Medical summary", height=105)
                d1, d2 = st.columns(2)
                with d1:
                    documents_provided = st.text_area("Documents provided", placeholder="Blood report, discharge summary…")
                with d2:
                    documents_required = st.text_area("Documents required", placeholder="ECG, previous scan…")
                submitted = st.form_submit_button("Create referral", type="primary", use_container_width=True)

            if submitted:
                if not patient_id.strip() or not reason.strip():
                    st.error("Patient ID and reason are required.")
                elif sending == receiving:
                    st.error("Choose different sending and receiving hospitals.")
                else:
                    add_referral(
                        patient_id.strip(), sending, receiving, reason.strip(),
                        summary.strip(), documents_provided.strip(), documents_required.strip()
                    )
                    st.success("Referral created.")
                    st.rerun()

        st.subheader("All referrals")
        current_referrals = get_referrals()
        if not current_referrals:
            st.info("No referrals yet. Create the first referral above.")
        for referral in current_referrals:
            show_referral(referral, doctor_mode=True)

    with tab2:
        st.subheader("Official medical history")
        st.caption("Only the doctor workspace can add or remove official entries.")
        history_patient_id = st.text_input("Patient ID", key="doctor_history_patient", placeholder="e.g. TEST-100")
        if history_patient_id.strip():
            show_official_history(history_patient_id.strip(), allow_edit=True)
            st.divider()
            with st.container(border=True):
                st.markdown("#### Add history entry")
                with st.form("doctor_history_form"):
                    entry = st.text_area("Clinician-reviewed history")
                    doctor_name = st.text_input("Doctor name", value="Doctor Demo")
                    save_history = st.form_submit_button("Save official history", type="primary")
                if save_history:
                    if not entry.strip() or not doctor_name.strip():
                        st.error("Enter both the history and doctor name.")
                    else:
                        add_medical_history(history_patient_id.strip(), entry.strip(), doctor_name.strip())
                        st.success("Official history saved.")
                        st.rerun()

    with tab3:
        st.subheader("Patient document review")
        st.caption("Patients and doctors can upload supporting documents. Doctor uploads are recorded as pending review too.")

        with st.container(border=True):
            st.markdown("#### Upload a document for a patient")
            with st.form("doctor_upload_form"):
                doctor_upload_patient_id = st.text_input(
                    "Patient ID for upload", key="doctor_upload_patient_id"
                )
                doctor_uploaded_file = st.file_uploader(
                    "Choose medical document",
                    type=["pdf", "png", "jpg", "jpeg"],
                    key="doctor_upload_file",
                    help="PDF or image up to 10 MB."
                )
                doctor_upload_submit = st.form_submit_button(
                    "Upload document", type="primary"
                )

            if doctor_upload_submit:
                if not doctor_upload_patient_id.strip():
                    st.error("Enter the patient ID.")
                elif doctor_uploaded_file is None:
                    st.error("Choose a file first.")
                elif doctor_uploaded_file.size > 10 * 1024 * 1024:
                    st.error("File exceeds the 10 MB demo limit.")
                else:
                    add_patient_upload(
                        doctor_upload_patient_id.strip(),
                        doctor_uploaded_file.name,
                        doctor_uploaded_file.type or "application/octet-stream",
                        doctor_uploaded_file.getvalue(),
                    )
                    st.success("Document uploaded to the patient's record.")
                    st.rerun()

        uploads = get_all_patient_uploads()
        if not uploads:
            st.info("No patient uploads yet.")
        for upload in uploads:
            upload_id, patient_id, file_name, content_type, uploaded_at, review_status = upload
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{file_name}**")
                    st.caption(f"Patient {patient_id} · Uploaded {uploaded_at}")
                with c2:
                    st.markdown(f"**{review_status}**")
                file_record = get_upload_file(upload_id)
                if file_record:
                    saved_name, saved_type, file_data = file_record
                    st.download_button(
                        "Download document", data=file_data, file_name=saved_name,
                        mime=saved_type or "application/octet-stream",
                        key=f"download_upload_{upload_id}",
                    )
                if review_status == "Pending":
                    if st.button("Mark reviewed", key=f"review_upload_{upload_id}"):
                        mark_upload_reviewed(upload_id)
                        st.rerun()

elif role == "Hospital":
    hospital = user["hospital"]
    brand()
    st.markdown('<div class="rl-eyebrow">HOSPITAL WORKSPACE</div>', unsafe_allow_html=True)
    st.title(f"{hospital} dashboard")
    st.markdown('<div class="rl-lead">Manage incoming handovers and track referrals sent by your facility.</div>', unsafe_allow_html=True)

    all_referrals = get_referrals()
    incoming = [r for r in all_referrals if r[3] == hospital]
    outgoing = [r for r in all_referrals if r[2] == hospital]

    m1, m2, m3 = st.columns(3)
    m1.metric("Incoming", len(incoming))
    m2.metric("Awaiting action", sum(r[6] in ("Sent", "Received") for r in incoming))
    m3.metric("Completed", sum(r[6] == "Completed" for r in incoming))

    tab1, tab2 = st.tabs(["Incoming referrals", "Outgoing referrals"])
    with tab1:
        if not incoming:
            st.info("No incoming referrals. Referrals addressed to this hospital will appear here.")
        for referral in incoming:
            show_referral(referral, hospital_mode=True)
    with tab2:
        if not outgoing:
            st.info("No outgoing referrals from this hospital.")
        for referral in outgoing:
            show_referral(referral)

elif role == "Patient":
    patient_id = user["patient_id"]
    brand()
    st.markdown('<div class="rl-eyebrow">PATIENT WORKSPACE</div>', unsafe_allow_html=True)
    st.title("Your care, connected.")
    st.markdown('<div class="rl-lead">View your referral progress, official medical history, and uploaded documents.</div>', unsafe_allow_html=True)

    patient_referrals = [r for r in get_referrals() if r[1] == patient_id]
    m1, m2, m3 = st.columns(3)
    m1.metric("Your referrals", len(patient_referrals))
    m2.metric("In progress", sum(r[6] not in ("Completed", "Rejected") for r in patient_referrals))
    m3.metric("Completed", sum(r[6] == "Completed" for r in patient_referrals))

    tab1, tab2, tab3 = st.tabs(["My referrals", "Medical history", "My documents"])
    with tab1:
        if not patient_referrals:
            st.info("No referrals found for this Patient ID.")
        for referral in patient_referrals:
            show_referral(referral)

    with tab2:
        st.subheader("Official medical history")
        st.caption("Your doctor maintains this record. You can view it but cannot edit or delete entries.")
        show_official_history(patient_id, allow_edit=False)

    with tab3:
        st.subheader("Upload medical history documents")
        st.caption("PDF or image, up to 10 MB. Uploaded files are sent for doctor review.")
        uploaded_file = st.file_uploader(
            "Choose a document",
            type=["pdf", "png", "jpg", "jpeg"],
        )
        if uploaded_file is not None:
            if uploaded_file.size > 10 * 1024 * 1024:
                st.error("The file exceeds the 10 MB demo limit.")
            elif st.button("Upload for doctor review", type="primary"):
                add_patient_upload(
                    patient_id, uploaded_file.name,
                    uploaded_file.type or "application/octet-stream",
                    uploaded_file.getvalue(),
                )
                st.success("Document uploaded for doctor review.")
                st.rerun()

        st.subheader("Your uploaded documents")
        uploads = get_patient_uploads(patient_id)
        if not uploads:
            st.info("You have not uploaded any documents yet.")
        for upload in uploads:
            upload_id, _, file_name, content_type, uploaded_at, review_status = upload
            with st.container(border=True):
                st.markdown(f"**{file_name}**")
                st.caption(f"Uploaded {uploaded_at} · Review status: {review_status}")
                file_record = get_upload_file(upload_id)
                if file_record:
                    saved_name, saved_type, file_data = file_record
                    st.download_button(
                        "Download my document", data=file_data, file_name=saved_name,
                        mime=saved_type or "application/octet-stream",
                        key=f"patient_download_{upload_id}",
                    )

st.markdown(
    '<div class="rl-footer">ReferralLoop · Hackathon prototype · Synthetic data only</div>',
    unsafe_allow_html=True,
)
