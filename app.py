
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
)

create_table()

# -----------------------------
# LOGIN
# -----------------------------

if "user" not in st.session_state:
    st.session_state.user = None

if "pending_delete" not in st.session_state:
    st.session_state.pending_delete = None

if "pending_history_delete" not in st.session_state:
    st.session_state.pending_history_delete = None

st.title("🏥 ReferralLoop")
st.caption("Patient Referral and Handover Platform")

if st.session_state.user is None:
    st.subheader("Welcome to ReferralLoop")
    st.write("Choose your demo account.")

    with st.form("login_form"):
        account = st.selectbox(
            "Login as",
            [
                "Doctor",
                "Hospital A",
                "Hospital B",
                "Hospital C",
                "Patient",
            ],
        )

        patient_id = ""

        if account == "Patient":
            patient_id = st.text_input("Patient ID")

        login_clicked = st.form_submit_button("Login")

    if login_clicked:
        if account == "Patient" and not patient_id.strip():
            st.error("Please enter your Patient ID.")
        else:
            if account == "Doctor":
                st.session_state.user = {"role": "Doctor"}

            elif account.startswith("Hospital"):
                st.session_state.user = {
                    "role": "Hospital",
                    "hospital": account,
                }

            else:
                st.session_state.user = {
                    "role": "Patient",
                    "patient_id": patient_id.strip(),
                }

            st.rerun()

    st.info(
        "Demo login only. Use fictional data. "
        "This prototype does not verify identities."
    )
    st.stop()

user = st.session_state.user
role = user["role"]

with st.sidebar:
    st.subheader("Current Account")
    st.write(f"**Role:** {role}")

    if role == "Hospital":
        st.write(f"**Facility:** {user['hospital']}")

    if role == "Patient":
        st.write(f"**Patient ID:** {user['patient_id']}")

    if st.button("Switch Account"):
        st.session_state.user = None
        st.rerun()


# -----------------------------
# SHARED DISPLAY FUNCTIONS
# -----------------------------

def show_history(referral_id):
    events = get_events(referral_id)

    if not events:
        st.info("No handover history recorded.")
        return

    for event_status, event_time, details in events:
        st.write(f"**{event_status}** | {event_time}")

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
            st.write(entry)
            st.caption(
                f"Recorded by {doctor_name} | {created_at}"
            )

            if allow_edit:
                if st.button(
                    "Delete History Entry",
                    key=f"delete_history_{history_id}",
                ):
                    st.session_state.pending_history_delete = history_id
                    st.rerun()

                if (
                    st.session_state.pending_history_delete
                    == history_id
                ):
                    st.warning("Confirm deletion of this entry.")

                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button(
                            "Confirm Delete",
                            key=f"confirm_history_{history_id}",
                        ):
                            delete_medical_history(history_id)
                            st.session_state.pending_history_delete = None
                            st.rerun()

                    with col2:
                        if st.button(
                            "Cancel",
                            key=f"cancel_history_{history_id}",
                        ):
                            st.session_state.pending_history_delete = None
                            st.rerun()


def show_referral(referral, hospital_mode=False, doctor_mode=False):
    (
        referral_id,
        patient_id,
        sending,
        receiving,
        reason,
        summary,
        status,
        documents_provided,
        documents_required,
    ) = referral

    with st.container(border=True):
        st.subheader(f"Referral #{referral_id}")
        st.write(f"**Patient ID:** {patient_id}")
        st.write(f"**From:** {sending} → **To:** {receiving}")
        st.write(f"**Reason:** {reason}")
        st.write(f"**Medical Summary:** {summary or 'Not provided'}")
        st.write(f"**Status:** {status}")
        st.write(
            "**Documents Provided:** "
            + (documents_provided or "None listed")
        )
        st.write(
            "**Documents Required:** "
            + (documents_required or "None listed")
        )

        can_act = (
            hospital_mode
            and receiving == user["hospital"]
        )

        if can_act:
            if status == "Sent":
                if st.button(
                    "Acknowledge Receipt",
                    key=f"receive_{referral_id}",
                ):
                    update_status(referral_id, "Received")
                    st.rerun()

            elif status == "Received":
                col1, col2 = st.columns(2)

                with col1:
                    if st.button(
                        "Accept Handover",
                        key=f"accept_{referral_id}",
                    ):
                        update_status(referral_id, "Accepted")
                        st.rerun()

                with col2:
                    with st.popover("Reject Referral"):
                        rejection_reason = st.text_area(
                            "Reason for rejection",
                            key=f"reject_reason_{referral_id}",
                        )

                        if st.button(
                            "Confirm Rejection",
                            key=f"confirm_reject_{referral_id}",
                        ):
                            if not rejection_reason.strip():
                                st.error("Enter a rejection reason.")
                            elif update_status(
                                referral_id,
                                "Rejected",
                                rejection_reason.strip(),
                            ):
                                st.success("Referral rejected.")
                                st.rerun()
                            else:
                                st.error("Could not update referral.")

            elif status == "Accepted":
                if st.button(
                    "Mark Outcome Documented",
                    key=f"complete_{referral_id}",
                ):
                    update_status(referral_id, "Completed")
                    st.rerun()

        if status == "Rejected":
            st.error("This referral was rejected.")
        elif status == "Completed":
            st.success("Referral workflow completed.")

        with st.expander("View Handover History"):
            show_history(referral_id)

        if doctor_mode:
            if st.button(
                "Delete Referral",
                key=f"delete_referral_{referral_id}",
            ):
                st.session_state.pending_delete = referral_id
                st.rerun()

            if st.session_state.pending_delete == referral_id:
                st.warning(
                    "This permanently deletes the referral and its history."
                )

                col1, col2 = st.columns(2)

                with col1:
                    if st.button(
                        "Confirm Delete",
                        key=f"confirm_delete_{referral_id}",
                    ):
                        delete_referral(referral_id)
                        st.session_state.pending_delete = None
                        st.rerun()

                with col2:
                    if st.button(
                        "Cancel",
                        key=f"cancel_delete_{referral_id}",
                    ):
                        st.session_state.pending_delete = None
                        st.rerun()


# -----------------------------
# DOCTOR DASHBOARD
# -----------------------------

if role == "Doctor":
    st.header("Doctor Dashboard")

    referrals = get_referrals()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Referrals", len(referrals))
    col2.metric("Awaiting Receipt", sum(r[6] == "Sent" for r in referrals))
    col3.metric("Rejected", sum(r[6] == "Rejected" for r in referrals))
    col4.metric("Completed", sum(r[6] == "Completed" for r in referrals))

    tab1, tab2, tab3 = st.tabs([
        "Create and Manage Referrals",
        "Official Medical History",
        "Patient Uploads",
    ])

    with tab1:
        st.subheader("Create a Referral")

        with st.form("create_referral_form"):
            patient_id = st.text_input("Patient ID")

            sending = st.selectbox(
                "Sending Hospital",
                ["Hospital A", "Hospital B", "Hospital C"],
            )

            receiving = st.selectbox(
                "Receiving Hospital",
                ["Hospital A", "Hospital B", "Hospital C"],
            )

            reason = st.text_input("Reason for Referral")
            summary = st.text_area("Medical Summary")

            documents_provided = st.text_area(
                "Documents Provided",
                placeholder="e.g. Blood report, discharge summary",
            )

            documents_required = st.text_area(
                "Documents Required",
                placeholder="e.g. ECG, previous scan",
            )

            submitted = st.form_submit_button("Create Referral")

        if submitted:
            if not patient_id.strip() or not reason.strip():
                st.error("Patient ID and referral reason are required.")
            elif sending == receiving:
                st.error("Choose a different receiving hospital.")
            else:
                add_referral(
                    patient_id.strip(),
                    sending,
                    receiving,
                    reason.strip(),
                    summary.strip(),
                    documents_provided.strip(),
                    documents_required.strip(),
                )
                st.success("Referral created successfully.")
                st.rerun()

        st.divider()
        st.subheader("All Referrals")

        current_referrals = get_referrals()

        if not current_referrals:
            st.info("No referrals have been created.")

        for referral in current_referrals:
            show_referral(referral, doctor_mode=True)

    with tab2:
        st.subheader("Official Medical History")
        st.caption(
            "Doctors can add or delete official history entries. "
            "Patient uploads do not automatically become official history."
        )

        history_patient_id = st.text_input(
            "Patient ID",
            key="doctor_history_patient",
        )

        if history_patient_id.strip():
            show_official_history(
                history_patient_id.strip(),
                allow_edit=True,
            )

            st.divider()
            st.subheader("Add Official History Entry")

            with st.form("doctor_history_form"):
                entry = st.text_area("Medical History Entry")
                doctor_name = st.text_input(
                    "Doctor Name",
                    value="Doctor Demo",
                )
                save_history = st.form_submit_button("Save History")

            if save_history:
                if not entry.strip() or not doctor_name.strip():
                    st.error("Enter both the history and doctor name.")
                else:
                    add_medical_history(
                        history_patient_id.strip(),
                        entry.strip(),
                        doctor_name.strip(),
                    )
                    st.success("Official history saved.")
                    st.rerun()

    with tab3:
        st.subheader("Review Patient Uploads")

        uploads = get_all_patient_uploads()

        if not uploads:
            st.info("No patient documents uploaded yet.")

        for upload in uploads:
            (
                upload_id,
                patient_id,
                file_name,
                content_type,
                uploaded_at,
                review_status,
            ) = upload

            with st.container(border=True):
                st.write(f"**Patient ID:** {patient_id}")
                st.write(f"**File:** {file_name}")
                st.write(f"**Uploaded:** {uploaded_at}")
                st.write(f"**Review Status:** {review_status}")

                file_record = get_upload_file(upload_id)

                if file_record:
                    saved_name, saved_type, file_data = file_record

                    st.download_button(
                        "Download Document",
                        data=file_data,
                        file_name=saved_name,
                        mime=saved_type or "application/octet-stream",
                        key=f"download_upload_{upload_id}",
                    )

                if review_status == "Pending":
                    if st.button(
                        "Mark as Reviewed",
                        key=f"review_upload_{upload_id}",
                    ):
                        mark_upload_reviewed(upload_id)
                        st.rerun()


# -----------------------------
# HOSPITAL DASHBOARD
# -----------------------------

elif role == "Hospital":
    hospital = user["hospital"]
    st.header(f"{hospital} Dashboard")

    all_referrals = get_referrals()

    incoming = [r for r in all_referrals if r[3] == hospital]
    outgoing = [r for r in all_referrals if r[2] == hospital]

    tab1, tab2 = st.tabs([
        "Incoming Referrals",
        "Outgoing Referrals",
    ])

    with tab1:
        if not incoming:
            st.info("No incoming referrals.")

        for referral in incoming:
            show_referral(referral, hospital_mode=True)

    with tab2:
        if not outgoing:
            st.info("No outgoing referrals.")

        for referral in outgoing:
            show_referral(referral)


# -----------------------------
# PATIENT DASHBOARD
# -----------------------------

elif role == "Patient":
    patient_id = user["patient_id"]

    st.header("Patient Dashboard")

    st.subheader("My Referrals")

    patient_referrals = [
        r for r in get_referrals() if r[1] == patient_id
    ]

    if not patient_referrals:
        st.info("No referrals found for this Patient ID.")

    for referral in patient_referrals:
        show_referral(referral)

    st.divider()
    st.subheader("My Official Medical History")
    st.caption(
        "This history is managed by the doctor. "
        "You can view it but cannot edit or delete entries."
    )

    show_official_history(patient_id, allow_edit=False)

    st.divider()
    st.subheader("Upload Medical History Documents")

    st.write(
        "Upload a supporting medical document for doctor review. "
        "Accepted formats: PDF, PNG, JPG, JPEG. Maximum size: 10 MB."
    )

    uploaded_file = st.file_uploader(
        "Choose a document",
        type=["pdf", "png", "jpg", "jpeg"],
        max_upload_size=10,
    )

    if uploaded_file is not None:
        if st.button("Upload for Doctor Review"):
            add_patient_upload(
                patient_id,
                uploaded_file.name,
                uploaded_file.type or "application/octet-stream",
                uploaded_file.getvalue(),
            )
            st.success("Document uploaded for doctor review.")
            st.rerun()

    st.subheader("My Uploaded Documents")

    uploads = get_patient_uploads(patient_id)

    if not uploads:
        st.info("You have not uploaded any documents yet.")

    for upload in uploads:
        (
            upload_id,
            _,
            file_name,
            content_type,
            uploaded_at,
            review_status,
        ) = upload

        with st.container(border=True):
            st.write(f"**{file_name}**")
            st.caption(
                f"Uploaded: {uploaded_at} | Review: {review_status}"
            )

            file_record = get_upload_file(upload_id)

            if file_record:
                saved_name, saved_type, file_data = file_record

                st.download_button(
                    "Download My Document",
                    data=file_data,
                    file_name=saved_name,
                    mime=saved_type or "application/octet-stream",
                    key=f"patient_download_{upload_id}",
                )
