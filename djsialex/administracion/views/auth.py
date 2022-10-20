from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User, Group
from django.contrib.sites.shortcuts import get_current_site
from django.forms import formset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib import messages
from django.db import IntegrityError, transaction

from ..forms import SignUpForm
from ..forms import EditProfileForm
from ..forms import PersonaContactoForm, BasePersonaContactoFormSet
from ..tokens import account_activation_token
from ..models import Profile, PersonaContacto, Pais, Region, Ciudad

import hashlib


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():

            user = form.save(commit=False)
            user.username = form.cleaned_data.get('email')
            user.is_active = False

            hs = (str(form.cleaned_data.get('numero_documento')))
            user.username = hs

            registrar = False

            usuario = User.objects.filter(username=user.username)

            if usuario.count() == 0:
                registrar = True

            userprofile = Profile.objects.filter(tipo_documento=form.cleaned_data.get('tipo_documento'),
                                                 numero_documento=form.cleaned_data.get('numero_documento'))

            if registrar:
                user.save()
                user.refresh_from_db()
                user.profile.tipo_documento = form.cleaned_data.get('tipo_documento')
                user.profile.numero_documento = form.cleaned_data.get('numero_documento')
                user.profile.primer_nombre = form.cleaned_data.get('primer_nombre').upper()
                user.profile.segundo_nombre = form.cleaned_data.get('segundo_nombre').upper()
                user.profile.primer_apellido = form.cleaned_data.get('primer_apellido').upper()
                user.profile.segundo_apellido = form.cleaned_data.get('segundo_apellido').upper()
                user.profile.fecha_nacimiento = form.cleaned_data.get('fecha_nacimiento')
                user.profile.acepta_habeas_data = form.cleaned_data.get('acepta_habeas_data')

                user.save()

                current_site = get_current_site(request)

                subject = 'Activar su cuenta de usuario en SIALEX'
                message = render_to_string('auth/account_activation_email.html', {
                    'user': user,
                    # 'domain': current_site.domain,
                    'domain': current_site,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)).encode().decode(),
                    'token': account_activation_token.make_token(user),
                })
                user.email_user(subject, message)

                return redirect('account_activation_sent')
            else:
                form.add_error('numero_documento', 'Usuario con Número de documento ya existente en base de datos')
        return render(request, 'auth/signup.html', {'form': form})
    elif request.method == 'GET':
        form = SignUpForm()
        return render(request, 'auth/signup.html', {'form': form})


def account_activation_sent(request):
    return render(request, 'auth/account_activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('complete-profile')
    else:
        return render(request, 'auth/account_activation_invalid.html')


def completeProfile(request):
    indc_fijo = ''
    perfil = get_object_or_404(Profile, usuario_id=request.user.id)
    PersonaContactoFormSet = formset_factory(PersonaContactoForm, formset=BasePersonaContactoFormSet, can_delete=True,
                                             extra=0, max_num=3, min_num=1, validate_max=True, validate_min=True)
    personas_contacto = PersonaContacto.objects.filter(profile=perfil).all()
    contactos = PersonaContacto.objects.filter(profile=perfil).order_by('nombres')
    datos_contactos = [{'nombres': c.nombres, 'apellidos': c.apellidos, 'numero_celular': c.numero_celular,
                        'correo_electronico': c.correo_electronico, 'parentesco': c.parentesco}
                       for c in contactos]

    if request.method == 'POST':

        form = EditProfileForm(request.POST, instance=perfil)
        persona_contacto_formset = PersonaContactoFormSet(request.POST)

        if form.is_valid() and persona_contacto_formset.is_valid():

            if 'telefono_fijo' in request.POST:
                indc_fijo = str(request.POST['telefono_fijo']).split('+')[0].upper()

            indc_celular = str(request.POST['telefono_celular']).split('+')[0].upper()
            profile = form.save(commit=False)
            profile.indicativo_fijo = indc_fijo
            profile.indicativo_celular = indc_celular
            profile.save()
            # se agrega el perfil de aspirante
            user = get_object_or_404(User, id=request.user.id)
            group = Group.objects.get(name='Aspirante')
            user.groups.add(group)
            user.save()

            nuevos_contactos = []

            for contacto_form in persona_contacto_formset:
                nombres = contacto_form.cleaned_data.get('nombres')
                apellidos = contacto_form.cleaned_data.get('apellidos')
                numero_celular = contacto_form.cleaned_data.get('numero_celular')
                correo_electronico = contacto_form.cleaned_data.get('correo_electronico')
                parentesco = contacto_form.cleaned_data.get('parentesco')

                if nombres and apellidos and numero_celular and correo_electronico and parentesco:
                    nuevos_contactos.append(PersonaContacto(nombres=nombres, apellidos=apellidos,
                                                            numero_celular=numero_celular,
                                                            correo_electronico=correo_electronico, profile=perfil,
                                                            parentesco=parentesco))

            try:
                with transaction.atomic():
                    # Replace the old with the new
                    PersonaContacto.objects.filter(profile=perfil).delete()
                    PersonaContacto.objects.bulk_create(nuevos_contactos)

                    # Notificacion de exito
                    messages.success(request, 'Se han guardado los cambios sobre su datos personales')

            except IntegrityError:  # If the transaction failed
                messages.error(request, 'Hubo un error al guardar sus datos personales')

            return redirect('home')
        form.indicativo_fijo = str(form.indicativo_fijo).lower()
        form.indicativo_celular = str(form.indicativo_celular).lower()
        return render(request, 'administracion/usuario/editarperfil.html', {'form': form,
                                                                            'persona_contacto_formset': persona_contacto_formset,
                                                                            })
    else:

        form = EditProfileForm(instance=perfil)
        p = Profile.objects.get(pk=perfil.id)
        form.indicativo_fijo = str(p.indicativo_fijo).lower()
        form.indicativo_celular = str(p.indicativo_celular).lower()

        persona_contacto_formset = PersonaContactoFormSet(initial=datos_contactos)

        return render(request, 'administracion/usuario/editarperfil.html', {'form': form,
                                                                            'persona_contacto_formset': persona_contacto_formset,
                                                                            'personas_contacto': personas_contacto,

                                                                            'ciudad_nacimiento': Ciudad.objects.get(
                                                                                pk=p.ciudad_nacimiento.id),
                                                                            'ciudad_residencia': Ciudad.objects.get(
                                                                                pk=p.ciudad_residencia.id),
                                                                            'ciudad_expedicion_documento': Ciudad.objects.get(
                                                                                pk=p.ciudad_expedicion_documento.id),
                                                                            })


def changeSelfUserPassword(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.add_message(request, messages.SUCCESS, 'La contraseña se ha actualizado correctamente')
            return redirect('change_password')
        else:
            messages.add_message(request, messages.WARNING, 'No se ha podido actualizar la contraseña')

    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'administracion/usuario/cambiarpassword.html', {
        'form': form
    })
