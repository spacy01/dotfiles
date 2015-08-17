;;; 40-python --- Python-specific stuff
;;; Commentary:
;;; Code:

(use-package virtualenvwrapper
  :ensure t
  :commands (venv-workon venv-deactivate venv-initialize-interactive-shells venv-initialize-eshell)
  :config
  (message "virtualenvwrapper loaded")
  :init
  (progn
    (setq venv-location "~/.virtualenvs")

    (defcustom python-venv nil
      "Name of the virtualenv to work on."
      :group 'python
      :safe #'stringp)

    (defun schnouki/setup-venv ()
      (hack-local-variables)
      (when python-venv
	(venv-workon python-venv)))
    (add-hook 'python-mode-hook 'schnouki/setup-venv)))

(use-package anaconda-mode
  :ensure t
  :commands anaconda-mode
  :diminish anaconda-mode
  :init
  (progn
    (add-hook 'python-mode-hook 'anaconda-mode)
    (add-hook 'python-mode-hook 'eldoc-mode)))

(use-package company-anaconda
  :ensure t
  :init (add-to-list 'company-backends 'company-anaconda))

(use-package company-inf-python
  :ensure t
  :init (add-to-list 'company-backends 'company-inf-python))

;; Django helper
(defun schnouki/use-django-interactive-shell ()
  "Auto-detect Django projects and change the interactive shell to `manage.py shell'."
  (interactive)
  (let ((file (buffer-file-name))
	(found nil))
    (while (not (or (null file)
		    (string= file "/")
		    found))
      (let* ((parent-dir (file-name-directory file))
	     (manage-py (concat parent-dir "manage.py")))
	(setq file (directory-file-name parent-dir))
	(when (file-exists-p manage-py)
	  (setq-local python-shell-interpreter-args (concat manage-py " shell"))
	  (setq found t))))))
(add-hook 'python-mode-hook 'schnouki/use-django-interactive-shell)

;; Pylint for Python 2
(flycheck-define-checker python2-pylint
  "A Python syntax and style checker using Pylint2."
  :command ("pylint2" "-r" "n"
	    "--msg-template" "{path}:{line}:{column}:{C}:{symbol}/{msg_id}:{msg}"
	    (config-file "--rcfile" flycheck-pylint2rc)
	    source-inplace)
  :error-filter
  (lambda (errors)
    (flycheck-sanitize-errors (flycheck-increment-error-columns errors)))
  :error-patterns
  ((error line-start (file-name) ":" line ":" column ":"
	  (or "E" "F") ":"
	  (id (one-or-more (not (any ":")))) ":"
	  (message) line-end)
   (warning line-start (file-name) ":" line ":" column ":"
	    (or "W" "R") ":"
	    (id (one-or-more (not (any ":")))) ":"
	    (message) line-end)
   (info line-start (file-name) ":" line ":" column ":"
	 "C:" (id (one-or-more (not (any ":")))) ":"
	 (message) line-end))
  :modes python-mode)
(flycheck-def-config-file-var flycheck-pylint2rc python2-pylint ".pylintrc"
  :safe #'stringp)
(add-to-list 'flycheck-checkers 'python2-pylint)

;;; init-40-python.el ends here
