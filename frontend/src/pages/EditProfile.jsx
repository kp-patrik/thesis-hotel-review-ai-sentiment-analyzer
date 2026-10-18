import React, { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";
import "./EditProfile.css";

const MAX_PHOTO_BYTES = 2 * 1024 * 1024;

export default function EditProfile() {
  const { user, updateUser } = useAuth();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [form, setForm] = useState({
    username: "",
    email: "",
    bio: "",
    current_password: "",
    new_password: "",
    confirm_password: "",
  });
  const [photo, setPhoto] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (user) {
      setForm((current) => ({
        ...current,
        username: user.username || "",
        email: user.email || "",
        bio: user.bio || "",
      }));
      setPhoto(user.profile_image_url || "");
    }
  }, [user]);

  const updateField = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const choosePhoto = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      setError("Please choose an image file.");
      return;
    }
    if (file.size > MAX_PHOTO_BYTES) {
      setError("Please choose an image smaller than 2 MB.");
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      setPhoto(reader.result);
      setError("");
    };
    reader.onerror = () => setError("The photo could not be read. Please try again.");
    reader.readAsDataURL(file);
  };

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    setSuccess("");
    if (form.new_password && form.new_password !== form.confirm_password) {
      setError("The new passwords do not match.");
      return;
    }
    if (form.new_password && !form.current_password) {
      setError("Enter your current password to set a new password.");
      return;
    }

    setSaving(true);
    try {
      const updatedUser = await updateUser({
        username: form.username.trim(),
        email: form.email.trim(),
        bio: form.bio.trim(),
        profile_image_url: photo,
        ...(form.new_password
          ? { current_password: form.current_password, new_password: form.new_password }
          : {}),
      });
      setForm((current) => ({ ...current, current_password: "", new_password: "", confirm_password: "" }));
      setSuccess("Your profile has been saved.");
      setTimeout(() => navigate("/profile"), 700);
      return updatedUser;
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "We could not save your profile.");
    } finally {
      setSaving(false);
    }
  };

  const initials = (form.username || "U").slice(0, 2).toUpperCase();

  return (
    <main className="edit-profile-page">
      <div className="edit-profile__heading">
        <div>
          <p className="edit-profile__eyebrow">Account settings</p>
          <h1>Edit your profile</h1>
          <p>Keep your public profile up to date for the hotel review community.</p>
        </div>
        <Link to="/profile" className="btn btn--outline">Cancel</Link>
      </div>

      <form className="edit-profile__layout" onSubmit={submit}>
        <section className="edit-profile__card edit-profile__identity">
          <div className="edit-profile__section-title">
            <div>
              <h2>Profile photo</h2>
              <p>Choose a clear image so other reviewers can recognize you.</p>
            </div>
          </div>
          <div className="edit-profile__photo-row">
            <div className="edit-profile__photo">
              {photo ? <img src={photo} alt="Profile preview" /> : initials}
            </div>
            <div>
              <button type="button" className="btn btn--primary" onClick={() => fileInputRef.current?.click()}>
                Upload photo
              </button>
              <button type="button" className="edit-profile__remove" onClick={() => { setPhoto(""); if (fileInputRef.current) fileInputRef.current.value = ""; }}>
                Remove
              </button>
              <input ref={fileInputRef} type="file" accept="image/*" onChange={choosePhoto} hidden />
              <small>JPG, PNG, or WebP. Maximum 2 MB.</small>
            </div>
          </div>
        </section>

        <section className="edit-profile__card">
          <div className="edit-profile__section-title">
            <div>
              <h2>Personal information</h2>
              <p>This information appears on your profile and reviews.</p>
            </div>
          </div>
          <div className="edit-profile__fields">
            <label>Username<input name="username" value={form.username} onChange={updateField} minLength="3" maxLength="50" required /></label>
            <label>Email address<input name="email" type="email" value={form.email} onChange={updateField} /></label>
            <label className="edit-profile__full">Bio <span>{form.bio.length}/280</span><textarea name="bio" value={form.bio} onChange={updateField} maxLength="280" rows="4" placeholder="Tell the community a little about yourself" /></label>
          </div>
        </section>

        <section className="edit-profile__card">
          <div className="edit-profile__section-title">
            <div>
              <h2>Change password</h2>
              <p>Leave these fields blank if you want to keep your current password.</p>
            </div>
          </div>
          <div className="edit-profile__fields">
            <label>Current password<input name="current_password" type="password" value={form.current_password} onChange={updateField} autoComplete="current-password" /></label>
            <label>New password<input name="new_password" type="password" value={form.new_password} onChange={updateField} minLength="6" autoComplete="new-password" /></label>
            <label>Confirm new password<input name="confirm_password" type="password" value={form.confirm_password} onChange={updateField} autoComplete="new-password" /></label>
          </div>
        </section>

        {error && <div className="edit-profile__message edit-profile__message--error">{error}</div>}
        {success && <div className="edit-profile__message edit-profile__message--success">{success}</div>}
        <div className="edit-profile__actions">
          <Link to="/profile" className="btn btn--outline">Cancel</Link>
          <button type="submit" className="btn btn--primary" disabled={saving}>{saving ? "Saving…" : "Save changes"}</button>
        </div>
      </form>
    </main>
  );
}
